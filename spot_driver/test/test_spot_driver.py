import contextlib
import unittest

import bdai_ros2_wrappers.scope as ros_scope
import rclpy
from bosdyn_msgs.msg import (
    ArmCommandFeedback,
    FullBodyCommandFeedback,
    GripperCommandFeedback,
    MobilityCommandFeedback,
    RobotCommandFeedback,
)
from std_srvs.srv import Trigger

import spot_driver.spot_ros2
from spot_driver.spot_ros2 import GoalResponse
from spot_msgs.srv import (  # type: ignore
    Dock,
)

FEEDBACK_INVALID = -128

def spin_thread(executor: MultiThreadedExecutor) -> None:
    if executor is not None:
        try:
            executor.spin()
        except (ExternalShutdownException, KeyboardInterrupt):
            pass


def call_trigger_client(
    client: rclpy.node.Client, executor: MultiThreadedExecutor, request: Any = Trigger.Request()
) -> spot_driver.spot_ros2.Response:
    req = request
    future = client.call_async(req)
    executor.spin_until_future_complete(future)
    resp = future.result()
    return resp


class SpotDriverTest(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = contextlib.ExitStack()
        self.ros = self.fixture.enter_context(ros_scope.top(namespace="fixture"))
        # create and run spot ros2 servers
        mock_param = rclpy.parameter.Parameter("spot_name", rclpy.Parameter.Type.STRING, "Mock_spot")
        self.spot_ros2 = self.ros.load(spot_driver.spot_ros2.SpotROS, parameter_list=[mock_param])

        # clients
        self.claim_client: rclpy.node.Client = self.ros.node.create_client(Trigger, "claim")
        self.release_client: rclpy.node.Client = self.ros.node.create_client(Trigger, "release")
        self.power_on_client: rclpy.node.Client = self.ros.node.create_client(Trigger, "power_on")
        self.power_off_client: rclpy.node.Client = self.ros.node.create_client(Trigger, "power_off")
        self.sit_client: rclpy.node.Client = self.ros.node.create_client(Trigger, "sit")
        self.stand_client: rclpy.node.Client = self.ros.node.create_client(Trigger, "stand")
        self.estop_gentle: rclpy.node.Client = self.ros.node.create_client(Trigger, "estop/gentle")
        self.estop_hard: rclpy.node.Client = self.ros.node.create_client(Trigger, "estop/hard")
        self.estop_release: rclpy.node.Client = self.ros.node.create_client(Trigger, "estop/release")
        self.undock_client: rclpy.node.Client = self.ros.node.create_client(Trigger, "undock")
        self.dock_client: rclpy.node.Client = self.ros.node.create_client(Dock, "dock")

    def tearDown(self) -> None:
        self.fixture.close()

    def test_wrapped_commands(self) -> None:
        """
        Spot Ros2 driver has multiple commands that are wrapped in a service wrapper.
        When no spot_wrapper is present they return true, but this test at least tests
        communications and APIs.
        """
        resp = self.claim_client.call(Trigger.Request())
        self.assertEqual(resp.success, True)
        resp = self.release_client.call(Trigger.Request())
        self.assertEqual(resp.success, True)

        resp = self.power_on_client.call(Trigger.Request())
        self.assertEqual(resp.success, True)
        resp = self.power_off_client.call(Trigger.Request())
        self.assertEqual(resp.success, True)
        resp = self.sit_client.call(Trigger.Request())
        self.assertEqual(resp.success, True)
        resp = self.stand_client.call(Trigger.Request())
        self.assertEqual(resp.success, True)
        resp = self.estop_hard.call(Trigger.Request())
        self.assertEqual(resp.success, True)
        resp = self.estop_gentle.call(Trigger.Request())
        self.assertEqual(resp.success, True)
        resp = self.estop_release.call(Trigger.Request())
        self.assertEqual(resp.success, True)
        resp = self.undock_client.call(Trigger.Request())
        self.assertEqual(resp.success, True)
        resp = self.dock_client.call(Dock.Request())
        self.assertEqual(resp.success, True)

    def test_process_full_body_command_feedback(self) -> None:
        feedback = FullBodyCommandFeedback()

        feedback.status.value = feedback.status.STATUS_UNKNOWN
        self.assertEqual(self.spot_ros2._process_full_body_command_feedback(feedback), GoalResponse.IN_PROGRESS)

        feedback.command.full_body_feedback.status.value = feedback.status.STATUS_PROCESSING

        """ Testing STOP_FEEDBACK_SET """
        feedback.command.full_body_feedback.feedback.feedback_choice = feedback.feedback.FEEDBACK_STOP_FEEDBACK_SET
        self.assertEqual(self.spot_ros2._process_full_body_command_feedback(feedback), GoalResponse.SUCCESS)

        """ Testing FREEZE_FEEDBACK_SET """
        feedback.command.full_body_feedback.feedback.feedback_choice = feedback.feedback.FEEDBACK_FREEZE_FEEDBACK_SET
        self.assertEqual(self.spot_ros2._process_full_body_command_feedback(feedback), GoalResponse.SUCCESS)

        """ Testing SELFRIGHT_FEEDBACK_SET """
        feedback.command.full_body_feedback.feedback.feedback_choice = feedback.feedback.FEEDBACK_SELFRIGHT_FEEDBACK_SET
        feedback.command.full_body_feedback.feedback.selfright_feedback.status.value = (
            feedback.feedback.selfright_feedback.status.STATUS_COMPLETED
        )
        self.assertEqual(self.spot_ros2._process_full_body_command_feedback(feedback), GoalResponse.SUCCESS)

        feedback.command.full_body_feedback.feedback.selfright_feedback.status.value = (
            feedback.feedback.selfright_feedback.status.STATUS_UNKNOWN
        )
        self.assertEqual(self.spot_ros2._process_full_body_command_feedback(feedback), GoalResponse.IN_PROGRESS)

        feedback.command.full_body_feedback.feedback.selfright_feedback.status.value = (
            feedback.feedback.selfright_feedback.status.STATUS_IN_PROGRESS
        )
        self.assertEqual(self.spot_ros2._process_full_body_command_feedback(feedback), GoalResponse.IN_PROGRESS)

        """ Testing SAFE_POWER_OFF_FEEDBACK_SET """
        feedback.command.full_body_feedback.feedback.feedback_choice = (
            feedback.feedback.FEEDBACK_SAFE_POWER_OFF_FEEDBACK_SET
        )
        feedback.command.full_body_feedback.feedback.safe_power_off_feedback.status.value = (
            feedback.feedback.safe_power_off_feedback.status.STATUS_POWERED_OFF
        )
        self.assertEqual(self.spot_ros2._process_full_body_command_feedback(feedback), GoalResponse.SUCCESS)

        feedback.command.full_body_feedback.feedback.safe_power_off_feedback.status.value = (
            feedback.feedback.safe_power_off_feedback.status.STATUS_UNKNOWN
        )
        self.assertEqual(self.spot_ros2._process_full_body_command_feedback(feedback), GoalResponse.IN_PROGRESS)

        feedback.command.full_body_feedback.feedback.safe_power_off_feedback.status.value = (
            feedback.feedback.safe_power_off_feedback.status.STATUS_IN_PROGRESS
        )
        self.assertEqual(self.spot_ros2._process_full_body_command_feedback(feedback), GoalResponse.IN_PROGRESS)

        """ Testing BATTERY_CHANGE_POSE_FEEDBACK_SET """
        feedback.command.full_body_feedback.feedback.feedback_choice = (
            feedback.feedback.FEEDBACK_BATTERY_CHANGE_POSE_FEEDBACK_SET
        )
        feedback.command.full_body_feedback.feedback.battery_change_pose_feedback.status.value = (
            feedback.feedback.battery_change_pose_feedback.status.STATUS_COMPLETED
        )
        self.assertEqual(self.spot_ros2._process_full_body_command_feedback(feedback), GoalResponse.SUCCESS)

        feedback.command.full_body_feedback.feedback.battery_change_pose_feedback.status.value = (
            feedback.feedback.battery_change_pose_feedback.status.STATUS_UNKNOWN
        )
        self.assertEqual(self.spot_ros2._process_full_body_command_feedback(feedback), GoalResponse.IN_PROGRESS)

        feedback.command.full_body_feedback.feedback.battery_change_pose_feedback.status.value = (
            feedback.feedback.battery_change_pose_feedback.status.STATUS_IN_PROGRESS
        )
        self.assertEqual(self.spot_ros2._process_full_body_command_feedback(feedback), GoalResponse.IN_PROGRESS)

        feedback.command.full_body_feedback.feedback.battery_change_pose_feedback.status.value = (
            feedback.feedback.battery_change_pose_feedback.status.STATUS_FAILED
        )
        self.assertEqual(self.spot_ros2._process_full_body_command_feedback(feedback), GoalResponse.FAILED)

        """ Testing PAYLOAD_ESTIMATION_FEEDBACK_SET """
        feedback.command.full_body_feedback.feedback.feedback_choice = (
            feedback.feedback.FEEDBACK_PAYLOAD_ESTIMATION_FEEDBACK_SET
        )
        feedback.command.full_body_feedback.feedback.payload_estimation_feedback.status.value = (
            feedback.feedback.payload_estimation_feedback.status.STATUS_COMPLETED
        )
        self.assertEqual(self.spot_ros2._process_full_body_command_feedback(feedback), GoalResponse.SUCCESS)

        feedback.command.full_body_feedback.feedback.payload_estimation_feedback.status.value = (
            feedback.feedback.payload_estimation_feedback.status.STATUS_SMALL_MASS
        )
        self.assertEqual(self.spot_ros2._process_full_body_command_feedback(feedback), GoalResponse.SUCCESS)

        feedback.command.full_body_feedback.feedback.payload_estimation_feedback.status.value = (
            feedback.feedback.payload_estimation_feedback.status.STATUS_ERROR
        )
        self.assertEqual(self.spot_ros2._process_full_body_command_feedback(feedback), GoalResponse.FAILED)

        feedback.command.full_body_feedback.feedback.payload_estimation_feedback.status.value = (
            feedback.feedback.payload_estimation_feedback.status.STATUS_UNKNOWN
        )
        self.assertEqual(self.spot_ros2._process_full_body_command_feedback(feedback), GoalResponse.IN_PROGRESS)

        feedback.command.full_body_feedback.feedback.payload_estimation_feedback.status.value = (
            feedback.feedback.payload_estimation_feedback.status.STATUS_IN_PROGRESS
        )
        self.assertEqual(self.spot_ros2._process_full_body_command_feedback(feedback), GoalResponse.IN_PROGRESS)

        """ Testing CONSTRAINED_MANIPULATION_FEEDBACK_SET """
        feedback.command.full_body_feedback.feedback.feedback_choice = (
            feedback.feedback.FEEDBACK_CONSTRAINED_MANIPULATION_FEEDBACK_SET
        )
        feedback.command.full_body_feedback.feedback.constrained_manipulation_feedback.status.value = (
            feedback.feedback.constrained_manipulation_feedback.status.STATUS_RUNNING
        )
        self.assertEqual(self.spot_ros2._process_full_body_command_feedback(feedback), GoalResponse.IN_PROGRESS)

        feedback.command.full_body_feedback.feedback.constrained_manipulation_feedback.status.value = (
            feedback.feedback.constrained_manipulation_feedback.status.STATUS_GRASP_IS_LOST
        )
        self.assertEqual(self.spot_ros2._process_full_body_command_feedback(feedback), GoalResponse.FAILED)

        feedback.command.full_body_feedback.feedback.constrained_manipulation_feedback.status.value = (
            feedback.feedback.constrained_manipulation_feedback.status.STATUS_ARM_IS_STUCK
        )
        self.assertEqual(self.spot_ros2._process_full_body_command_feedback(feedback), GoalResponse.FAILED)

        feedback.command.full_body_feedback.feedback.constrained_manipulation_feedback.status.value = (
            feedback.feedback.constrained_manipulation_feedback.status.STATUS_UNKNOWN
        )
        self.assertEqual(self.spot_ros2._process_full_body_command_feedback(feedback), GoalResponse.FAILED)

    def test_process_synchronized_arm_command_feedback(self) -> None:
        feedback = ArmCommandFeedback()

        feedback.status.value = feedback.status.STATUS_COMMAND_OVERRIDDEN

        self.assertEqual(self.spot_ros2._process_synchronized_arm_command_feedback(feedback), GoalResponse.FAILED)

        feedback.status.value = feedback.status.STATUS_COMMAND_TIMED_OUT
        self.assertEqual(self.spot_ros2._process_synchronized_arm_command_feedback(feedback), GoalResponse.FAILED)

        feedback.status.value = feedback.status.STATUS_ROBOT_FROZEN
        self.assertEqual(self.spot_ros2._process_synchronized_arm_command_feedback(feedback), GoalResponse.FAILED)

        feedback.status.value = feedback.status.STATUS_INCOMPATIBLE_HARDWARE
        self.assertEqual(self.spot_ros2._process_synchronized_arm_command_feedback(feedback), GoalResponse.FAILED)

        feedback.status.value = feedback.status.STATUS_PROCESSING

        """ Testing arm cartesian feedback """
        feedback.feedback.feedback_choice = feedback.feedback.FEEDBACK_ARM_CARTESIAN_FEEDBACK_SET

        feedback.feedback.arm_cartesian_feedback.status.value = (
            feedback.feedback.arm_cartesian_feedback.status.STATUS_TRAJECTORY_COMPLETE
        )
        self.assertEqual(self.spot_ros2._process_synchronized_arm_command_feedback(feedback), GoalResponse.SUCCESS)

        feedback.feedback.arm_cartesian_feedback.status.value = (
            feedback.feedback.arm_cartesian_feedback.status.STATUS_UNKNOWN
        )
        self.assertEqual(self.spot_ros2._process_synchronized_arm_command_feedback(feedback), GoalResponse.IN_PROGRESS)

        feedback.feedback.arm_cartesian_feedback.status.value = (
            feedback.feedback.arm_cartesian_feedback.status.STATUS_IN_PROGRESS
        )
        self.assertEqual(self.spot_ros2._process_synchronized_arm_command_feedback(feedback), GoalResponse.IN_PROGRESS)

        # Should this status return a GoalResponse.FAILED?
        feedback.feedback.arm_cartesian_feedback.status.value = (
            feedback.feedback.arm_cartesian_feedback.status.STATUS_TRAJECTORY_CANCELLED
        )
        self.assertEqual(self.spot_ros2._process_synchronized_arm_command_feedback(feedback), GoalResponse.IN_PROGRESS)
        # Should this status return a GoalResponse.FAILED?
        feedback.feedback.arm_cartesian_feedback.status.value = (
            feedback.feedback.arm_cartesian_feedback.status.STATUS_TRAJECTORY_STALLED
        )
        self.assertEqual(self.spot_ros2._process_synchronized_arm_command_feedback(feedback), GoalResponse.IN_PROGRESS)

        """ Testing arm joint move feedback """
        feedback.feedback.feedback_choice = feedback.feedback.FEEDBACK_ARM_JOINT_MOVE_FEEDBACK_SET

        feedback.feedback.arm_joint_move_feedback.status.value = (
            feedback.feedback.arm_joint_move_feedback.status.STATUS_COMPLETE
        )
        self.assertEqual(self.spot_ros2._process_synchronized_arm_command_feedback(feedback), GoalResponse.SUCCESS)

        feedback.feedback.arm_joint_move_feedback.status.value = (
            feedback.feedback.arm_joint_move_feedback.status.STATUS_UNKNOWN
        )
        self.assertEqual(self.spot_ros2._process_synchronized_arm_command_feedback(feedback), GoalResponse.IN_PROGRESS)

        feedback.feedback.arm_joint_move_feedback.status.value = (
            feedback.feedback.arm_joint_move_feedback.status.STATUS_IN_PROGRESS
        )
        self.assertEqual(self.spot_ros2._process_synchronized_arm_command_feedback(feedback), GoalResponse.IN_PROGRESS)

        # Should this status return a GoalResponse.FAILED?
        feedback.feedback.arm_joint_move_feedback.status.value = (
            feedback.feedback.arm_joint_move_feedback.status.STATUS_STALLED
        )
        self.assertEqual(self.spot_ros2._process_synchronized_arm_command_feedback(feedback), GoalResponse.IN_PROGRESS)

        """ Testing named arm position feedback """
        feedback.feedback.feedback_choice = feedback.feedback.FEEDBACK_NAMED_ARM_POSITION_FEEDBACK_SET

        feedback.feedback.named_arm_position_feedback.status.value = (
            feedback.feedback.named_arm_position_feedback.status.STATUS_COMPLETE
        )
        self.assertEqual(self.spot_ros2._process_synchronized_arm_command_feedback(feedback), GoalResponse.SUCCESS)

        feedback.feedback.named_arm_position_feedback.status.value = (
            feedback.feedback.named_arm_position_feedback.status.STATUS_UNKNOWN
        )
        self.assertEqual(self.spot_ros2._process_synchronized_arm_command_feedback(feedback), GoalResponse.IN_PROGRESS)

        feedback.feedback.named_arm_position_feedback.status.value = (
            feedback.feedback.named_arm_position_feedback.status.STATUS_IN_PROGRESS
        )
        self.assertEqual(self.spot_ros2._process_synchronized_arm_command_feedback(feedback), GoalResponse.IN_PROGRESS)

        # Should this status return a GoalResponse.FAILED?
        feedback.feedback.named_arm_position_feedback.status.value = (
            feedback.feedback.named_arm_position_feedback.status.STATUS_STALLED_HOLDING_ITEM
        )
        self.assertEqual(self.spot_ros2._process_synchronized_arm_command_feedback(feedback), GoalResponse.IN_PROGRESS)

        """ Testing arm velocity feedback """
        feedback.feedback.feedback_choice = feedback.feedback.FEEDBACK_ARM_VELOCITY_FEEDBACK_SET
        self.assertEqual(self.spot_ros2._process_synchronized_arm_command_feedback(feedback), None)

        """ Testing arm gaze feedback """
        feedback.feedback.feedback_choice = feedback.feedback.FEEDBACK_ARM_GAZE_FEEDBACK_SET

        feedback.feedback.arm_gaze_feedback.status.value = (
            feedback.feedback.arm_gaze_feedback.status.STATUS_TRAJECTORY_COMPLETE
        )
        self.assertEqual(self.spot_ros2._process_synchronized_arm_command_feedback(feedback), GoalResponse.SUCCESS)

        feedback.feedback.arm_gaze_feedback.status.value = feedback.feedback.arm_gaze_feedback.status.STATUS_UNKNOWN
        self.assertEqual(self.spot_ros2._process_synchronized_arm_command_feedback(feedback), GoalResponse.IN_PROGRESS)

        feedback.feedback.arm_gaze_feedback.status.value = feedback.feedback.arm_gaze_feedback.status.STATUS_IN_PROGRESS
        self.assertEqual(self.spot_ros2._process_synchronized_arm_command_feedback(feedback), GoalResponse.IN_PROGRESS)

        # Should this status return a GoalResponse.FAILED?
        feedback.feedback.arm_gaze_feedback.status.value = (
            feedback.feedback.arm_gaze_feedback.status.STATUS_TOOL_TRAJECTORY_STALLED
        )
        self.assertEqual(self.spot_ros2._process_synchronized_arm_command_feedback(feedback), GoalResponse.IN_PROGRESS)

        """ Testing arm stop feedback """
        feedback.feedback.feedback_choice = feedback.feedback.FEEDBACK_ARM_STOP_FEEDBACK_SET

        self.assertEqual(self.spot_ros2._process_synchronized_arm_command_feedback(feedback), None)

        """ Testing arm drag feedback """
        feedback.feedback.feedback_choice = feedback.feedback.FEEDBACK_ARM_DRAG_FEEDBACK_SET

        feedback.feedback.arm_drag_feedback.status.value = feedback.feedback.arm_drag_feedback.status.STATUS_DRAGGING
        self.assertEqual(self.spot_ros2._process_synchronized_arm_command_feedback(feedback), GoalResponse.SUCCESS)

        feedback.feedback.arm_drag_feedback.status.value = feedback.feedback.arm_drag_feedback.status.STATUS_UNKNOWN
        self.assertEqual(self.spot_ros2._process_synchronized_arm_command_feedback(feedback), GoalResponse.FAILED)

        feedback.feedback.arm_drag_feedback.status.value = (
            feedback.feedback.arm_drag_feedback.status.STATUS_GRASP_FAILED
        )
        self.assertEqual(self.spot_ros2._process_synchronized_arm_command_feedback(feedback), GoalResponse.FAILED)

        feedback.feedback.arm_drag_feedback.status.value = (
            feedback.feedback.arm_drag_feedback.status.STATUS_OTHER_FAILURE
        )
        self.assertEqual(self.spot_ros2._process_synchronized_arm_command_feedback(feedback), GoalResponse.FAILED)

        """ Testing arm drag feedback """
        feedback.feedback.feedback_choice = feedback.feedback.FEEDBACK_ARM_IMPEDANCE_FEEDBACK_SET

        self.assertEqual(self.spot_ros2._process_synchronized_arm_command_feedback(feedback), None)

        """ Testing arm Impedance feedback """
        feedback.feedback.feedback_choice = feedback.feedback.FEEDBACK_ARM_IMPEDANCE_FEEDBACK_SET
        self.assertEqual(self.spot_ros2._process_synchronized_arm_command_feedback(feedback), None)

        feedback.feedback.feedback_choice = feedback.feedback.FEEDBACK_NOT_SET

        self.assertEqual(self.spot_ros2._process_synchronized_arm_command_feedback(feedback), None)

        """ Testing unknown arm command """
        feedback.feedback.feedback_choice = FEEDBACK_INVALID

        self.assertEqual(self.spot_ros2._process_synchronized_arm_command_feedback(feedback), GoalResponse.IN_PROGRESS)

    def test_process_synchronized_mobility_command_feedback(self) -> None:
        """Testing mobility commands"""
        feedback = MobilityCommandFeedback()

        feedback.status.value = feedback.status.STATUS_COMMAND_OVERRIDDEN
        self.assertEqual(self.spot_ros2._process_synchronized_mobility_command_feedback(feedback), GoalResponse.FAILED)

        feedback.status.value = feedback.status.STATUS_COMMAND_TIMED_OUT
        self.assertEqual(self.spot_ros2._process_synchronized_mobility_command_feedback(feedback), GoalResponse.FAILED)

        feedback.status.value = feedback.status.STATUS_ROBOT_FROZEN
        self.assertEqual(self.spot_ros2._process_synchronized_mobility_command_feedback(feedback), GoalResponse.FAILED)

        feedback.status.value = feedback.status.STATUS_INCOMPATIBLE_HARDWARE
        self.assertEqual(self.spot_ros2._process_synchronized_mobility_command_feedback(feedback), GoalResponse.FAILED)

        feedback.status.value = feedback.status.STATUS_PROCESSING

        """ Testing se2 trajectory feedback """
        feedback.feedback.feedback_choice = feedback.feedback.FEEDBACK_SE2_TRAJECTORY_FEEDBACK_SET

        feedback.feedback.se2_trajectory_feedback.status.value = (
            feedback.feedback.se2_trajectory_feedback.status.STATUS_AT_GOAL
        )
        self.assertEqual(self.spot_ros2._process_synchronized_mobility_command_feedback(feedback), GoalResponse.SUCCESS)

        feedback.feedback.se2_trajectory_feedback.status.value = (
            feedback.feedback.se2_trajectory_feedback.status.STATUS_UNKNOWN
        )
        self.assertEqual(
            self.spot_ros2._process_synchronized_mobility_command_feedback(feedback), GoalResponse.IN_PROGRESS
        )

        feedback.feedback.se2_trajectory_feedback.status.value = (
            feedback.feedback.se2_trajectory_feedback.status.STATUS_NEAR_GOAL
        )
        self.assertEqual(
            self.spot_ros2._process_synchronized_mobility_command_feedback(feedback), GoalResponse.IN_PROGRESS
        )

        feedback.feedback.se2_trajectory_feedback.status.value = (
            feedback.feedback.se2_trajectory_feedback.status.STATUS_GOING_TO_GOAL
        )
        self.assertEqual(
            self.spot_ros2._process_synchronized_mobility_command_feedback(feedback), GoalResponse.IN_PROGRESS
        )

        """ Testing se2 velocity feedback """
        feedback.feedback.feedback_choice = feedback.feedback.FEEDBACK_SE2_VELOCITY_FEEDBACK_SET
        self.assertEqual(self.spot_ros2._process_synchronized_mobility_command_feedback(feedback), None)

        """ Testing sit feedback """
        feedback.feedback.feedback_choice = feedback.feedback.FEEDBACK_SIT_FEEDBACK_SET

        feedback.feedback.sit_feedback.status.value = feedback.feedback.sit_feedback.status.STATUS_IS_SITTING
        self.assertEqual(self.spot_ros2._process_synchronized_mobility_command_feedback(feedback), GoalResponse.SUCCESS)

        feedback.feedback.sit_feedback.status.value = feedback.feedback.sit_feedback.status.STATUS_UNKNOWN
        self.assertEqual(
            self.spot_ros2._process_synchronized_mobility_command_feedback(feedback), GoalResponse.IN_PROGRESS
        )

        feedback.feedback.sit_feedback.status.value = feedback.feedback.sit_feedback.status.STATUS_IN_PROGRESS
        self.assertEqual(
            self.spot_ros2._process_synchronized_mobility_command_feedback(feedback), GoalResponse.IN_PROGRESS
        )

        """ Testing stand feedback """
        feedback.feedback.feedback_choice = feedback.feedback.FEEDBACK_STAND_FEEDBACK_SET

        feedback.feedback.stand_feedback.status.value = feedback.feedback.stand_feedback.status.STATUS_IS_STANDING
        self.assertEqual(self.spot_ros2._process_synchronized_mobility_command_feedback(feedback), GoalResponse.SUCCESS)

        feedback.feedback.stand_feedback.status.value = feedback.feedback.stand_feedback.status.STATUS_UNKNOWN
        self.assertEqual(
            self.spot_ros2._process_synchronized_mobility_command_feedback(feedback), GoalResponse.IN_PROGRESS
        )

        feedback.feedback.stand_feedback.status.value = feedback.feedback.stand_feedback.status.STATUS_IN_PROGRESS
        self.assertEqual(
            self.spot_ros2._process_synchronized_mobility_command_feedback(feedback), GoalResponse.IN_PROGRESS
        )

        """ Testing stance feedback """
        feedback.feedback.feedback_choice = feedback.feedback.FEEDBACK_STANCE_FEEDBACK_SET

        feedback.feedback.stance_feedback.status.value = feedback.feedback.stance_feedback.status.STATUS_TOO_FAR_AWAY
        self.assertEqual(self.spot_ros2._process_synchronized_mobility_command_feedback(feedback), GoalResponse.FAILED)

        feedback.feedback.stance_feedback.status.value = feedback.feedback.stance_feedback.status.STATUS_STANCED
        self.assertEqual(self.spot_ros2._process_synchronized_mobility_command_feedback(feedback), GoalResponse.SUCCESS)

        feedback.feedback.stance_feedback.status.value = feedback.feedback.stance_feedback.status.STATUS_GOING_TO_STANCE
        self.assertEqual(
            self.spot_ros2._process_synchronized_mobility_command_feedback(feedback), GoalResponse.IN_PROGRESS
        )

        feedback.feedback.stance_feedback.status.value = feedback.feedback.stance_feedback.status.STATUS_UNKNOWN
        self.assertEqual(
            self.spot_ros2._process_synchronized_mobility_command_feedback(feedback), GoalResponse.IN_PROGRESS
        )

        """ Testing stop feedback """
        feedback.feedback.feedback_choice = feedback.feedback.FEEDBACK_STOP_FEEDBACK_SET

        self.assertEqual(self.spot_ros2._process_synchronized_mobility_command_feedback(feedback), None)

        """ Testing Follow arm feedback """
        feedback.feedback.feedback_choice = feedback.feedback.FEEDBACK_FOLLOW_ARM_FEEDBACK_SET

        self.assertEqual(self.spot_ros2._process_synchronized_mobility_command_feedback(feedback), None)

        """ Testing feedback not set"""
        feedback.feedback.feedback_choice = feedback.feedback.FEEDBACK_NOT_SET

        self.assertEqual(self.spot_ros2._process_synchronized_mobility_command_feedback(feedback), None)

        """ Testing unknown command """
        feedback.feedback.feedback_choice = FEEDBACK_INVALID
        self.assertEqual(
            self.spot_ros2._process_synchronized_mobility_command_feedback(feedback), GoalResponse.IN_PROGRESS
        )

    def test_process_synchronized_gripper_command_feedback(self) -> None:
        """Testing Gripper commands"""
        feedback = GripperCommandFeedback()

        feedback.status.value = feedback.status.STATUS_COMMAND_OVERRIDDEN
        self.assertEqual(self.spot_ros2._process_synchronized_gripper_command_feedback(feedback), GoalResponse.FAILED)

        feedback.status.value = feedback.status.STATUS_COMMAND_TIMED_OUT
        self.assertEqual(self.spot_ros2._process_synchronized_gripper_command_feedback(feedback), GoalResponse.FAILED)

        feedback.status.value = feedback.status.STATUS_ROBOT_FROZEN
        self.assertEqual(self.spot_ros2._process_synchronized_gripper_command_feedback(feedback), GoalResponse.FAILED)

        feedback.status.value = feedback.status.STATUS_INCOMPATIBLE_HARDWARE
        self.assertEqual(self.spot_ros2._process_synchronized_gripper_command_feedback(feedback), GoalResponse.FAILED)

        feedback.status.value = feedback.status.STATUS_PROCESSING

        """ Testing Claw Gripper feedback """
        feedback.command.command_choice = feedback.command.COMMAND_CLAW_GRIPPER_FEEDBACK_SET
        feedback.command.claw_gripper_feedback.status.value = (
            feedback.command.claw_gripper_feedback.status.STATUS_IN_PROGRESS
        )
        self.assertEqual(
            self.spot_ros2._process_synchronized_gripper_command_feedback(feedback), GoalResponse.IN_PROGRESS
        )

        feedback.command.claw_gripper_feedback.status.value = (
            feedback.command.claw_gripper_feedback.status.STATUS_UNKNOWN
        )
        self.assertEqual(
            self.spot_ros2._process_synchronized_gripper_command_feedback(feedback), GoalResponse.IN_PROGRESS
        )

        feedback.command.claw_gripper_feedback.status.value = (
            feedback.command.claw_gripper_feedback.status.STATUS_AT_GOAL
        )
        self.assertEqual(self.spot_ros2._process_synchronized_gripper_command_feedback(feedback), None)

        feedback.command.claw_gripper_feedback.status.value = (
            feedback.command.claw_gripper_feedback.status.STATUS_APPLYING_FORCE
        )
        self.assertEqual(self.spot_ros2._process_synchronized_gripper_command_feedback(feedback), None)

        """ Testing feedback not set"""
        feedback.feedback.feedback_choice = feedback.feedback.FEEDBACK_NOT_SET

        self.assertEqual(self.spot_ros2._process_synchronized_gripper_command_feedback(feedback), None)

        """ Testing unknown gripper command """
        feedback.command.command_choice = FEEDBACK_INVALID
        self.assertEqual(
            self.spot_ros2._process_synchronized_gripper_command_feedback(feedback), GoalResponse.IN_PROGRESS
        )

    def test_robot_command_goal_complete(self) -> None:
        self.assertEqual(self.spot_ros2._robot_command_goal_complete(None), GoalResponse.IN_PROGRESS)

        feedback = RobotCommandFeedback()

        feedback.command.command_choice = feedback.command.COMMAND_FULL_BODY_FEEDBACK_SET

        """ Testing Synchronized Feedback Command """

        feedback.command.command_choice = feedback.command.COMMAND_SYNCHRONIZED_FEEDBACK_SET

        """ Testing unknown robot command type """
        feedback.command.command_choice = FEEDBACK_INVALID
        self.assertEqual(self.spot_ros2._robot_command_goal_complete(feedback), GoalResponse.IN_PROGRESS)


if __name__ == "__main__":
    unittest.main()

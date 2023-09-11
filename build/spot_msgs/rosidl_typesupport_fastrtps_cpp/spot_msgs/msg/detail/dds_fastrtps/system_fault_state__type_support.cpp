// generated from rosidl_typesupport_fastrtps_cpp/resource/idl__type_support.cpp.em
// with input from spot_msgs:msg/SystemFaultState.idl
// generated code does not contain a copyright notice
#include "spot_msgs/msg/detail/system_fault_state__rosidl_typesupport_fastrtps_cpp.hpp"
#include "spot_msgs/msg/detail/system_fault_state__struct.hpp"

#include <limits>
#include <stdexcept>
#include <string>
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_fastrtps_cpp/identifier.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_fastrtps_cpp/wstring_conversion.hpp"
#include "fastcdr/Cdr.h"


// forward declaration of message dependencies and their conversion functions
namespace spot_msgs
{
namespace msg
{
namespace typesupport_fastrtps_cpp
{
bool cdr_serialize(
  const spot_msgs::msg::SystemFault &,
  eprosima::fastcdr::Cdr &);
bool cdr_deserialize(
  eprosima::fastcdr::Cdr &,
  spot_msgs::msg::SystemFault &);
size_t get_serialized_size(
  const spot_msgs::msg::SystemFault &,
  size_t current_alignment);
size_t
max_serialized_size_SystemFault(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);
}  // namespace typesupport_fastrtps_cpp
}  // namespace msg
}  // namespace spot_msgs

// functions for spot_msgs::msg::SystemFault already declared above


namespace spot_msgs
{

namespace msg
{

namespace typesupport_fastrtps_cpp
{

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_spot_msgs
cdr_serialize(
  const spot_msgs::msg::SystemFaultState & ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Member: faults
  {
    size_t size = ros_message.faults.size();
    cdr << static_cast<uint32_t>(size);
    for (size_t i = 0; i < size; i++) {
      spot_msgs::msg::typesupport_fastrtps_cpp::cdr_serialize(
        ros_message.faults[i],
        cdr);
    }
  }
  // Member: historical_faults
  {
    size_t size = ros_message.historical_faults.size();
    cdr << static_cast<uint32_t>(size);
    for (size_t i = 0; i < size; i++) {
      spot_msgs::msg::typesupport_fastrtps_cpp::cdr_serialize(
        ros_message.historical_faults[i],
        cdr);
    }
  }
  return true;
}

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_spot_msgs
cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  spot_msgs::msg::SystemFaultState & ros_message)
{
  // Member: faults
  {
    uint32_t cdrSize;
    cdr >> cdrSize;
    size_t size = static_cast<size_t>(cdrSize);
    ros_message.faults.resize(size);
    for (size_t i = 0; i < size; i++) {
      spot_msgs::msg::typesupport_fastrtps_cpp::cdr_deserialize(
        cdr, ros_message.faults[i]);
    }
  }

  // Member: historical_faults
  {
    uint32_t cdrSize;
    cdr >> cdrSize;
    size_t size = static_cast<size_t>(cdrSize);
    ros_message.historical_faults.resize(size);
    for (size_t i = 0; i < size; i++) {
      spot_msgs::msg::typesupport_fastrtps_cpp::cdr_deserialize(
        cdr, ros_message.historical_faults[i]);
    }
  }

  return true;
}

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_spot_msgs
get_serialized_size(
  const spot_msgs::msg::SystemFaultState & ros_message,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Member: faults
  {
    size_t array_size = ros_message.faults.size();

    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);

    for (size_t index = 0; index < array_size; ++index) {
      current_alignment +=
        spot_msgs::msg::typesupport_fastrtps_cpp::get_serialized_size(
        ros_message.faults[index], current_alignment);
    }
  }
  // Member: historical_faults
  {
    size_t array_size = ros_message.historical_faults.size();

    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);

    for (size_t index = 0; index < array_size; ++index) {
      current_alignment +=
        spot_msgs::msg::typesupport_fastrtps_cpp::get_serialized_size(
        ros_message.historical_faults[index], current_alignment);
    }
  }

  return current_alignment - initial_alignment;
}

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_spot_msgs
max_serialized_size_SystemFaultState(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  full_bounded = true;
  is_plain = true;


  // Member: faults
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);


    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      current_alignment +=
        spot_msgs::msg::typesupport_fastrtps_cpp::max_serialized_size_SystemFault(
        inner_full_bounded, inner_is_plain, current_alignment);
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Member: historical_faults
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);


    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      current_alignment +=
        spot_msgs::msg::typesupport_fastrtps_cpp::max_serialized_size_SystemFault(
        inner_full_bounded, inner_is_plain, current_alignment);
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  return current_alignment - initial_alignment;
}

static bool _SystemFaultState__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  auto typed_message =
    static_cast<const spot_msgs::msg::SystemFaultState *>(
    untyped_ros_message);
  return cdr_serialize(*typed_message, cdr);
}

static bool _SystemFaultState__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  auto typed_message =
    static_cast<spot_msgs::msg::SystemFaultState *>(
    untyped_ros_message);
  return cdr_deserialize(cdr, *typed_message);
}

static uint32_t _SystemFaultState__get_serialized_size(
  const void * untyped_ros_message)
{
  auto typed_message =
    static_cast<const spot_msgs::msg::SystemFaultState *>(
    untyped_ros_message);
  return static_cast<uint32_t>(get_serialized_size(*typed_message, 0));
}

static size_t _SystemFaultState__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_SystemFaultState(full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}

static message_type_support_callbacks_t _SystemFaultState__callbacks = {
  "spot_msgs::msg",
  "SystemFaultState",
  _SystemFaultState__cdr_serialize,
  _SystemFaultState__cdr_deserialize,
  _SystemFaultState__get_serialized_size,
  _SystemFaultState__max_serialized_size
};

static rosidl_message_type_support_t _SystemFaultState__handle = {
  rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
  &_SystemFaultState__callbacks,
  get_message_typesupport_handle_function,
};

}  // namespace typesupport_fastrtps_cpp

}  // namespace msg

}  // namespace spot_msgs

namespace rosidl_typesupport_fastrtps_cpp
{

template<>
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_EXPORT_spot_msgs
const rosidl_message_type_support_t *
get_message_type_support_handle<spot_msgs::msg::SystemFaultState>()
{
  return &spot_msgs::msg::typesupport_fastrtps_cpp::_SystemFaultState__handle;
}

}  // namespace rosidl_typesupport_fastrtps_cpp

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, spot_msgs, msg, SystemFaultState)() {
  return &spot_msgs::msg::typesupport_fastrtps_cpp::_SystemFaultState__handle;
}

#ifdef __cplusplus
}
#endif

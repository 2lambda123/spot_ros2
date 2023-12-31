FROM ros:humble-ros-base-jammy

SHELL ["/bin/bash", "-c"]

# setup environment
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

# install packages
RUN apt-get update \
    && apt-get install -q -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

ARG ROS_DISTRO=humble
ENV ROS_DISTRO $ROS_DISTRO
ARG INSTALL_PACKAGE=base

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN DEBIAN_FRONTEND=noninteractive apt-get update -q && \
    apt-get update -q && \
    apt-get install -yq --no-install-recommends \
    python3-pip \
    python-is-python3 \
    python3-argcomplete \
    python3-colcon-common-extensions \
    python3-colcon-mixin \
    python3-pytest-cov \
    python3-rosdep \
    libpython3-dev \
    python3-vcstool \
    ros-humble-tl-expected && \
    rm -rf /var/lib/apt/lists/*

# I added this
RUN source "/opt/ros/${ROS_DISTRO}/setup.bash"

# Spot packages
RUN apt-get update -q && \
    apt-get install -y --no-install-recommends \
    ros-${ROS_DISTRO}-joint-state-publisher-gui \
    ros-${ROS_DISTRO}-depth-image-proc \
    ros-${ROS_DISTRO}-vision-msgs \
    ros-${ROS_DISTRO}-interactive-markers && \
    rm -rf /var/lib/apt/lists/*

# Install bosdyn_msgs package
RUN curl -sL https://github.com/bdaiinstitute/bosdyn_msgs/releases/download/v3.2.0-frametreesnapshot/ros-humble-bosdyn-msgs_3.2.0-0jammy_amd64.deb --output /tmp/ros-humble-bosdyn-msgs_3.2.0-0jammy_amd64.deb --silent \
  && dpkg -i /tmp/ros-humble-bosdyn-msgs_3.2.0-0jammy_amd64.deb \
  && rm /tmp/ros-humble-bosdyn-msgs_3.2.0-0jammy_amd64.deb

# Install spot_cpp_sdk package
RUN curl -sL https://github.com/bdaiinstitute/spot-cpp-sdk/releases/download/v3.3.0-cmake-infra/spot-cpp-sdk_3.3.0_amd64.deb --output /tmp/spot-cpp-sdk_3.3.0_amd64.deb --silent \
  && dpkg -i /tmp/spot-cpp-sdk_3.3.0_amd64.deb \
  && rm /tmp/spot-cpp-sdk_3.3.0_amd64.deb

# Install packages inside the new environment
RUN python -m pip install --no-cache-dir --upgrade pip==22.3.1 \
    && pip install --root-user-action=ignore --no-cache-dir --default-timeout=900 \
    numpy==1.24.1 \
    bosdyn-client==3.3.2 \
    bosdyn-mission==3.3.2 \
    bosdyn-api==3.3.2 \
    bosdyn-core==3.3.2  && \
    pip cache purge

# ROS doesn't recognize the docker shells as terminals so force colored output
ENV RCUTILS_COLORIZED_OUTPUT=1

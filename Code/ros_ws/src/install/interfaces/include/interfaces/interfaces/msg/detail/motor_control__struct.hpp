// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from interfaces:msg/MotorControl.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "interfaces/msg/motor_control.hpp"


#ifndef INTERFACES__MSG__DETAIL__MOTOR_CONTROL__STRUCT_HPP_
#define INTERFACES__MSG__DETAIL__MOTOR_CONTROL__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__interfaces__msg__MotorControl __attribute__((deprecated))
#else
# define DEPRECATED__interfaces__msg__MotorControl __declspec(deprecated)
#endif

namespace interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct MotorControl_
{
  using Type = MotorControl_<ContainerAllocator>;

  explicit MotorControl_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->motor1_speed = 0.0;
      this->motor1_direction = false;
      this->motor2_speed = 0.0;
      this->motor2_direction = false;
    }
  }

  explicit MotorControl_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->motor1_speed = 0.0;
      this->motor1_direction = false;
      this->motor2_speed = 0.0;
      this->motor2_direction = false;
    }
  }

  // field types and members
  using _motor1_speed_type =
    double;
  _motor1_speed_type motor1_speed;
  using _motor1_direction_type =
    bool;
  _motor1_direction_type motor1_direction;
  using _motor2_speed_type =
    double;
  _motor2_speed_type motor2_speed;
  using _motor2_direction_type =
    bool;
  _motor2_direction_type motor2_direction;

  // setters for named parameter idiom
  Type & set__motor1_speed(
    const double & _arg)
  {
    this->motor1_speed = _arg;
    return *this;
  }
  Type & set__motor1_direction(
    const bool & _arg)
  {
    this->motor1_direction = _arg;
    return *this;
  }
  Type & set__motor2_speed(
    const double & _arg)
  {
    this->motor2_speed = _arg;
    return *this;
  }
  Type & set__motor2_direction(
    const bool & _arg)
  {
    this->motor2_direction = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    interfaces::msg::MotorControl_<ContainerAllocator> *;
  using ConstRawPtr =
    const interfaces::msg::MotorControl_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<interfaces::msg::MotorControl_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<interfaces::msg::MotorControl_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      interfaces::msg::MotorControl_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<interfaces::msg::MotorControl_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      interfaces::msg::MotorControl_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<interfaces::msg::MotorControl_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<interfaces::msg::MotorControl_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<interfaces::msg::MotorControl_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__interfaces__msg__MotorControl
    std::shared_ptr<interfaces::msg::MotorControl_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__interfaces__msg__MotorControl
    std::shared_ptr<interfaces::msg::MotorControl_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const MotorControl_ & other) const
  {
    if (this->motor1_speed != other.motor1_speed) {
      return false;
    }
    if (this->motor1_direction != other.motor1_direction) {
      return false;
    }
    if (this->motor2_speed != other.motor2_speed) {
      return false;
    }
    if (this->motor2_direction != other.motor2_direction) {
      return false;
    }
    return true;
  }
  bool operator!=(const MotorControl_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct MotorControl_

// alias to use template instance with default allocator
using MotorControl =
  interfaces::msg::MotorControl_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace interfaces

#endif  // INTERFACES__MSG__DETAIL__MOTOR_CONTROL__STRUCT_HPP_

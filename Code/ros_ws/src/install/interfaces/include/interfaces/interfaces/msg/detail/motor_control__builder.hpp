// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from interfaces:msg/MotorControl.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "interfaces/msg/motor_control.hpp"


#ifndef INTERFACES__MSG__DETAIL__MOTOR_CONTROL__BUILDER_HPP_
#define INTERFACES__MSG__DETAIL__MOTOR_CONTROL__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "interfaces/msg/detail/motor_control__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace interfaces
{

namespace msg
{

namespace builder
{

class Init_MotorControl_motor2_direction
{
public:
  explicit Init_MotorControl_motor2_direction(::interfaces::msg::MotorControl & msg)
  : msg_(msg)
  {}
  ::interfaces::msg::MotorControl motor2_direction(::interfaces::msg::MotorControl::_motor2_direction_type arg)
  {
    msg_.motor2_direction = std::move(arg);
    return std::move(msg_);
  }

private:
  ::interfaces::msg::MotorControl msg_;
};

class Init_MotorControl_motor2_speed
{
public:
  explicit Init_MotorControl_motor2_speed(::interfaces::msg::MotorControl & msg)
  : msg_(msg)
  {}
  Init_MotorControl_motor2_direction motor2_speed(::interfaces::msg::MotorControl::_motor2_speed_type arg)
  {
    msg_.motor2_speed = std::move(arg);
    return Init_MotorControl_motor2_direction(msg_);
  }

private:
  ::interfaces::msg::MotorControl msg_;
};

class Init_MotorControl_motor1_direction
{
public:
  explicit Init_MotorControl_motor1_direction(::interfaces::msg::MotorControl & msg)
  : msg_(msg)
  {}
  Init_MotorControl_motor2_speed motor1_direction(::interfaces::msg::MotorControl::_motor1_direction_type arg)
  {
    msg_.motor1_direction = std::move(arg);
    return Init_MotorControl_motor2_speed(msg_);
  }

private:
  ::interfaces::msg::MotorControl msg_;
};

class Init_MotorControl_motor1_speed
{
public:
  Init_MotorControl_motor1_speed()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_MotorControl_motor1_direction motor1_speed(::interfaces::msg::MotorControl::_motor1_speed_type arg)
  {
    msg_.motor1_speed = std::move(arg);
    return Init_MotorControl_motor1_direction(msg_);
  }

private:
  ::interfaces::msg::MotorControl msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::interfaces::msg::MotorControl>()
{
  return interfaces::msg::builder::Init_MotorControl_motor1_speed();
}

}  // namespace interfaces

#endif  // INTERFACES__MSG__DETAIL__MOTOR_CONTROL__BUILDER_HPP_

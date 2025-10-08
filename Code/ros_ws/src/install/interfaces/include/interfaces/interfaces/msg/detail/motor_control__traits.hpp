// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from interfaces:msg/MotorControl.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "interfaces/msg/motor_control.hpp"


#ifndef INTERFACES__MSG__DETAIL__MOTOR_CONTROL__TRAITS_HPP_
#define INTERFACES__MSG__DETAIL__MOTOR_CONTROL__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "interfaces/msg/detail/motor_control__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const MotorControl & msg,
  std::ostream & out)
{
  out << "{";
  // member: motor1_speed
  {
    out << "motor1_speed: ";
    rosidl_generator_traits::value_to_yaml(msg.motor1_speed, out);
    out << ", ";
  }

  // member: motor1_direction
  {
    out << "motor1_direction: ";
    rosidl_generator_traits::value_to_yaml(msg.motor1_direction, out);
    out << ", ";
  }

  // member: motor2_speed
  {
    out << "motor2_speed: ";
    rosidl_generator_traits::value_to_yaml(msg.motor2_speed, out);
    out << ", ";
  }

  // member: motor2_direction
  {
    out << "motor2_direction: ";
    rosidl_generator_traits::value_to_yaml(msg.motor2_direction, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const MotorControl & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: motor1_speed
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "motor1_speed: ";
    rosidl_generator_traits::value_to_yaml(msg.motor1_speed, out);
    out << "\n";
  }

  // member: motor1_direction
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "motor1_direction: ";
    rosidl_generator_traits::value_to_yaml(msg.motor1_direction, out);
    out << "\n";
  }

  // member: motor2_speed
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "motor2_speed: ";
    rosidl_generator_traits::value_to_yaml(msg.motor2_speed, out);
    out << "\n";
  }

  // member: motor2_direction
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "motor2_direction: ";
    rosidl_generator_traits::value_to_yaml(msg.motor2_direction, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const MotorControl & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace interfaces

namespace rosidl_generator_traits
{

[[deprecated("use interfaces::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const interfaces::msg::MotorControl & msg,
  std::ostream & out, size_t indentation = 0)
{
  interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const interfaces::msg::MotorControl & msg)
{
  return interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<interfaces::msg::MotorControl>()
{
  return "interfaces::msg::MotorControl";
}

template<>
inline const char * name<interfaces::msg::MotorControl>()
{
  return "interfaces/msg/MotorControl";
}

template<>
struct has_fixed_size<interfaces::msg::MotorControl>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<interfaces::msg::MotorControl>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<interfaces::msg::MotorControl>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // INTERFACES__MSG__DETAIL__MOTOR_CONTROL__TRAITS_HPP_

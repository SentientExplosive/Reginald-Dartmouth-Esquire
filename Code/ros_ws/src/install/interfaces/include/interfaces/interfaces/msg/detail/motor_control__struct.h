// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from interfaces:msg/MotorControl.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "interfaces/msg/motor_control.h"


#ifndef INTERFACES__MSG__DETAIL__MOTOR_CONTROL__STRUCT_H_
#define INTERFACES__MSG__DETAIL__MOTOR_CONTROL__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

/// Struct defined in msg/MotorControl in the package interfaces.
typedef struct interfaces__msg__MotorControl
{
  double motor1_speed;
  bool motor1_direction;
  double motor2_speed;
  bool motor2_direction;
} interfaces__msg__MotorControl;

// Struct for a sequence of interfaces__msg__MotorControl.
typedef struct interfaces__msg__MotorControl__Sequence
{
  interfaces__msg__MotorControl * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} interfaces__msg__MotorControl__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // INTERFACES__MSG__DETAIL__MOTOR_CONTROL__STRUCT_H_

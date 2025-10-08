// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from interfaces:msg/MotorControl.idl
// generated code does not contain a copyright notice

#include "interfaces/msg/detail/motor_control__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_interfaces
const rosidl_type_hash_t *
interfaces__msg__MotorControl__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0xdf, 0xc0, 0x77, 0x86, 0x7f, 0x73, 0xbb, 0x5e,
      0x72, 0x16, 0x9c, 0x51, 0x97, 0x38, 0x39, 0x4c,
      0x1f, 0x79, 0xaa, 0x4e, 0xaa, 0x13, 0xa0, 0xe0,
      0x11, 0x71, 0x50, 0xd2, 0x40, 0x59, 0xe8, 0xfb,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char interfaces__msg__MotorControl__TYPE_NAME[] = "interfaces/msg/MotorControl";

// Define type names, field names, and default values
static char interfaces__msg__MotorControl__FIELD_NAME__motor1_speed[] = "motor1_speed";
static char interfaces__msg__MotorControl__FIELD_NAME__motor1_direction[] = "motor1_direction";
static char interfaces__msg__MotorControl__FIELD_NAME__motor2_speed[] = "motor2_speed";
static char interfaces__msg__MotorControl__FIELD_NAME__motor2_direction[] = "motor2_direction";

static rosidl_runtime_c__type_description__Field interfaces__msg__MotorControl__FIELDS[] = {
  {
    {interfaces__msg__MotorControl__FIELD_NAME__motor1_speed, 12, 12},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_DOUBLE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {interfaces__msg__MotorControl__FIELD_NAME__motor1_direction, 16, 16},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_BOOLEAN,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {interfaces__msg__MotorControl__FIELD_NAME__motor2_speed, 12, 12},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_DOUBLE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {interfaces__msg__MotorControl__FIELD_NAME__motor2_direction, 16, 16},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_BOOLEAN,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
interfaces__msg__MotorControl__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {interfaces__msg__MotorControl__TYPE_NAME, 27, 27},
      {interfaces__msg__MotorControl__FIELDS, 4, 4},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "float64 motor1_speed\n"
  "bool motor1_direction\n"
  "float64 motor2_speed\n"
  "bool motor2_direction";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
interfaces__msg__MotorControl__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {interfaces__msg__MotorControl__TYPE_NAME, 27, 27},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 86, 86},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
interfaces__msg__MotorControl__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *interfaces__msg__MotorControl__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}

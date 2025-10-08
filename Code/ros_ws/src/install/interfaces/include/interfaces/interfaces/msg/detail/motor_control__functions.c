// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from interfaces:msg/MotorControl.idl
// generated code does not contain a copyright notice
#include "interfaces/msg/detail/motor_control__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


bool
interfaces__msg__MotorControl__init(interfaces__msg__MotorControl * msg)
{
  if (!msg) {
    return false;
  }
  // motor1_speed
  // motor1_direction
  // motor2_speed
  // motor2_direction
  return true;
}

void
interfaces__msg__MotorControl__fini(interfaces__msg__MotorControl * msg)
{
  if (!msg) {
    return;
  }
  // motor1_speed
  // motor1_direction
  // motor2_speed
  // motor2_direction
}

bool
interfaces__msg__MotorControl__are_equal(const interfaces__msg__MotorControl * lhs, const interfaces__msg__MotorControl * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // motor1_speed
  if (lhs->motor1_speed != rhs->motor1_speed) {
    return false;
  }
  // motor1_direction
  if (lhs->motor1_direction != rhs->motor1_direction) {
    return false;
  }
  // motor2_speed
  if (lhs->motor2_speed != rhs->motor2_speed) {
    return false;
  }
  // motor2_direction
  if (lhs->motor2_direction != rhs->motor2_direction) {
    return false;
  }
  return true;
}

bool
interfaces__msg__MotorControl__copy(
  const interfaces__msg__MotorControl * input,
  interfaces__msg__MotorControl * output)
{
  if (!input || !output) {
    return false;
  }
  // motor1_speed
  output->motor1_speed = input->motor1_speed;
  // motor1_direction
  output->motor1_direction = input->motor1_direction;
  // motor2_speed
  output->motor2_speed = input->motor2_speed;
  // motor2_direction
  output->motor2_direction = input->motor2_direction;
  return true;
}

interfaces__msg__MotorControl *
interfaces__msg__MotorControl__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  interfaces__msg__MotorControl * msg = (interfaces__msg__MotorControl *)allocator.allocate(sizeof(interfaces__msg__MotorControl), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(interfaces__msg__MotorControl));
  bool success = interfaces__msg__MotorControl__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
interfaces__msg__MotorControl__destroy(interfaces__msg__MotorControl * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    interfaces__msg__MotorControl__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
interfaces__msg__MotorControl__Sequence__init(interfaces__msg__MotorControl__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  interfaces__msg__MotorControl * data = NULL;

  if (size) {
    data = (interfaces__msg__MotorControl *)allocator.zero_allocate(size, sizeof(interfaces__msg__MotorControl), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = interfaces__msg__MotorControl__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        interfaces__msg__MotorControl__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
interfaces__msg__MotorControl__Sequence__fini(interfaces__msg__MotorControl__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      interfaces__msg__MotorControl__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

interfaces__msg__MotorControl__Sequence *
interfaces__msg__MotorControl__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  interfaces__msg__MotorControl__Sequence * array = (interfaces__msg__MotorControl__Sequence *)allocator.allocate(sizeof(interfaces__msg__MotorControl__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = interfaces__msg__MotorControl__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
interfaces__msg__MotorControl__Sequence__destroy(interfaces__msg__MotorControl__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    interfaces__msg__MotorControl__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
interfaces__msg__MotorControl__Sequence__are_equal(const interfaces__msg__MotorControl__Sequence * lhs, const interfaces__msg__MotorControl__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!interfaces__msg__MotorControl__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
interfaces__msg__MotorControl__Sequence__copy(
  const interfaces__msg__MotorControl__Sequence * input,
  interfaces__msg__MotorControl__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(interfaces__msg__MotorControl);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    interfaces__msg__MotorControl * data =
      (interfaces__msg__MotorControl *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!interfaces__msg__MotorControl__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          interfaces__msg__MotorControl__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!interfaces__msg__MotorControl__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}

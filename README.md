# FastAPI Practice

This repository contains two practical examples using FastAPI and Pydantic to demonstrate fundamental REST API operations, including data validation, JSON file handling, and advanced Pydantic features.

This is not a production system, but a learning exercise focused on core concepts.

## 1. Patient Management API

The first code implements a simple patient management API using FastAPI. Data is stored in a local `patients.json` file, acting as a lightweight database.

### Implemented Features

The API supports the following operations:

* Create a patient (`POST /create`)
* View all patients (`GET /view`)
* View a patient by ID (`GET /patient/{patient_id}`)
* Update a patient (`PUT /edit/{patient_id}`)
* Delete a patient (`DELETE /delete/{patient_id}`)
* Sort patients by height, weight, or BMI (`GET /sort`)

### Data Validation

The `Patient` model includes:

* Field constraints (`gt`, `lt`)
* `Literal` types to restrict allowed values
* `Annotated` for metadata and documentation
* `computed_field` for automatic calculation of:

  * BMI
  * Health verdict (underweight, normal, overweight, obese)

A `PatientUpdate` model allows partial updates using optional fields and `exclude_unset=True`.

### Persistence Layer

The application:

* Loads data from `patients.json`
* Modifies data in memory
* Saves changes back to the JSON file after write operations

This example demonstrates route creation, request validation, error handling with `HTTPException`, query parameters, and basic file-based persistence.

---

## 2. Advanced Pydantic Validation Example

The second code focuses on advanced data validation features using Pydantic.

### Implemented Concepts

This example includes:

* Nested models (`Address`)
* Built-in types such as:

  * `EmailStr`
  * `AnyUrl`
* Field constraints (`max_length`, `gt`, `strict`)
* Optional fields with complex types (`List`, `Dict`)
* Custom validators:

  * `field_validator` for email domain validation
  * Name transformation (automatic uppercase conversion)
  * Age validation
* `model_validator` for cross-field validation (e.g., requiring emergency contact for patients older than 60)
* `computed_field` for BMI calculation

It also demonstrates:

* Model instantiation from dictionaries
* Automatic type coercion
* JSON serialization using:

  * `model_dump_json()`
  * `include`
  * `exclude`
  * Nested field exclusion

---

## Purpose

The goal of this repository is to practice:

* FastAPI route development
* Pydantic model design
* Data validation techniques
* Computed fields
* Partial updates
* Basic persistence strategies

These examples provide a structured foundation for building more robust and production-ready APIs in the future.

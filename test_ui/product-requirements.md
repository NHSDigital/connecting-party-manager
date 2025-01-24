# Product Creation System Requirements

## 1. Overview

### 1.1 Purpose

This document specifies the requirements for a two-step web-based system for creating Product Teams and Products following NHS Digital design standards.

### 1.2 Scope

The system encompasses:

- Product Team creation interface
- Product creation interface
- API integration
- User feedback mechanisms
- Form validation
- Response handling

## 2. User Interface Requirements

### 2.1 General Layout

- Follow NHS Digital design system guidelines
- NHS blue header (color code: #005EB8)
- White content area with shadow
- Dark gray footer
- Maximum width of 1280px (max-w-7xl)
- Responsive design for all screen sizes

### 2.2 Common Elements

- NHS logo in header
- Dynamic page title based on current step
- Error message area at top of content
- Form fields with labels
- Success message area
- Response data display area
- Copyright footer

## 3. Step 1: Product Team Creation

### 3.1 Form Fields

1. ODS Code Field

   - Required field
   - Text input
   - Label: "ODS Code"
   - No whitespace trimming during input
   - Validation: Must not be empty

2. Team Name Field
   - Required field
   - Text input
   - Label: "Team Name"
   - No whitespace trimming during input
   - Validation: Must not be empty

### 3.2 Buttons

1. Create Product Team Button

   - Initial state: disabled
   - Enabled when both fields have non-empty values
   - Disabled during API call
   - Disabled after successful creation
   - Text states:
     - Normal: "Create Product Team"
     - Loading: "Creating..."

2. Next Button
   - Initial state: disabled
   - Enabled only after successful team creation
   - Navigates to Product creation step when clicked
   - Text: "Next"

### 3.3 API Integration

1. Request Payload:

   ```json
   {
     "ods_code": "YEA",
     "name": "test team"
   }
   ```

2. Expected Response:
   ```json
   {
     "id": "YEA.f55686f4-6ee3-4851-9b67-686df78953f0",
     "name": "test team",
     "ods_code": "YEA",
     "status": "active",
     "created_on": "2025-01-23T09:40:44.088568+00:00",
     "updated_on": null,
     "deleted_on": null,
     "keys": []
   }
   ```

### 3.4 Post-Creation Behavior

1. Form fields convert to read-only text displays
2. Display success message: "Product Team created successfully"
3. Show complete API response data
4. Enable Next button
5. Disable Create Product Team button

## 4. Step 2: Product Creation

### 4.1 Form Fields

1. Name Field
   - Required field
   - Text input
   - Label: "Name"
   - No whitespace trimming during input
   - Validation: Must not be empty

### 4.2 Buttons

1. Create Product Button
   - Initial state: disabled
   - Enabled when name field has non-empty value
   - Disabled during API call
   - Disabled after successful creation
   - Text states:
     - Normal: "Create Product"
     - Loading: "Creating..."

### 4.3 API Integration

1. Request Payload:

   ```json
   {
     "name": "test product 2"
   }
   ```

2. Expected Response:
   ```json
   {
     "id": "P.MWV-7AA",
     "product_team_id": "YEA.f55686f4-6ee3-4851-9b67-686df78953f0",
     "name": "test product 2",
     "ods_code": "YEA",
     "status": "active",
     "created_on": "2025-01-23T09:43:17.549506+00:00",
     "updated_on": null,
     "deleted_on": null,
     "keys": []
   }
   ```

### 4.4 Post-Creation Behavior

1. Form field converts to read-only text display
2. Display success message: "Product created successfully"
3. Show complete API response data
4. Disable Create Product button

## 5. Error Handling

### 5.1 Form Validation Errors

- Prevent submission when required fields are empty
- Maintain button disabled states until requirements met
- No error messages for empty fields (handled through button states)

### 5.2 API Errors

1. Product Team Creation

   - Display error message: "Failed to create Product Team. Please try again."
   - Maintain form in editable state
   - Clear loading state
   - Allow retry

2. Product Creation
   - Display error message: "Failed to create Product. Please try again."
   - Maintain form in editable state
   - Clear loading state
   - Allow retry

## 6. State Management

### 6.1 Form States

1. Initial State

   - Empty form fields
   - Disabled submission buttons
   - No error messages
   - No success messages

2. Loading State

   - Disabled form fields
   - Loading button text
   - Disabled buttons
   - No error messages

3. Success State

   - Read-only form fields
   - Success message visible
   - Response data visible
   - Appropriate button states

4. Error State
   - Editable form fields
   - Error message visible
   - Enabled submission button (if fields valid)
   - No success message

## 7. Performance Requirements

### 7.1 Response Times

- Form field updates: Immediate
- Button state updates: Immediate
- API call timeout: 30 seconds
- Page navigation: Immediate
- Field conversion (to read-only): Immediate

### 7.2 Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Responsive design for mobile devices
- Graceful degradation for older browsers

## 8. Security Requirements

### 8.1 Input Validation

- Client-side validation for required fields
- No script injection in form fields
- API response sanitization before display

### 8.2 Data Handling

- No local storage of sensitive data
- Clear form state on page refresh
- Secure API communication (HTTPS)

## 9. Accessibility Requirements

### 9.1 Form Accessibility

- Proper label associations
- Keyboard navigation
- Clear focus states
- Appropriate ARIA attributes
- Color contrast compliance

### 9.2 Error Accessibility

- Error messages linked to form fields
- Color-independent error states
- Screen reader compatibility

## 10. Documentation Requirements

### 10.1 Code Documentation

- Component purpose and structure
- State management explanation
- API integration details
- Error handling procedures
- Button state logic

### 10.2 User Documentation

- Step-by-step usage guide
- Error message explanations
- Expected behaviors
- API response explanations

## Appendix A: Design System References

### A.1 NHS Digital Design System

- Color palette
- Typography
- Spacing
- Component styles
- Form patterns

### A.2 API Response Formats

- Detailed request/response examples
- Field descriptions
- Error response formats
- Status codes

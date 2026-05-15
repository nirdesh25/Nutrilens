/**
 * Input Component Examples
 * 
 * This file demonstrates various use cases of the Input component.
 */

import React, { useState } from 'react';
import { Input } from './Input';

export function InputExamples() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [age, setAge] = useState('');
  const [emailError, setEmailError] = useState('');

  const validateEmail = (value: string) => {
    if (!value) {
      setEmailError('Email is required');
    } else if (!/\S+@\S+\.\S+/.test(value)) {
      setEmailError('Invalid email format');
    } else {
      setEmailError('');
    }
  };

  return (
    <div className="space-y-6 p-6 max-w-md">
      <h2 className="text-2xl font-bold mb-4">Input Component Examples</h2>

      {/* Basic text input */}
      <div>
        <h3 className="text-lg font-semibold mb-2">Basic Text Input</h3>
        <Input
          type="text"
          placeholder="Enter your name"
        />
      </div>

      {/* Input with label */}
      <div>
        <h3 className="text-lg font-semibold mb-2">Input with Label</h3>
        <Input
          type="text"
          label="Full Name"
          placeholder="John Doe"
        />
      </div>

      {/* Email input with validation */}
      <div>
        <h3 className="text-lg font-semibold mb-2">Email with Validation</h3>
        <Input
          type="email"
          label="Email Address"
          placeholder="user@example.com"
          value={email}
          onChange={(e) => {
            setEmail(e.target.value);
            validateEmail(e.target.value);
          }}
          onBlur={(e) => validateEmail(e.target.value)}
          error={emailError}
        />
      </div>

      {/* Password input */}
      <div>
        <h3 className="text-lg font-semibold mb-2">Password Input</h3>
        <Input
          type="password"
          label="Password"
          placeholder="Enter your password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </div>

      {/* Number input */}
      <div>
        <h3 className="text-lg font-semibold mb-2">Number Input</h3>
        <Input
          type="number"
          label="Age"
          placeholder="Enter your age"
          value={age}
          onChange={(e) => setAge(e.target.value)}
          min={0}
          max={120}
        />
      </div>

      {/* Input with error state */}
      <div>
        <h3 className="text-lg font-semibold mb-2">Input with Error</h3>
        <Input
          type="text"
          label="Username"
          placeholder="Enter username"
          error="This username is already taken"
        />
      </div>

      {/* Disabled input */}
      <div>
        <h3 className="text-lg font-semibold mb-2">Disabled Input</h3>
        <Input
          type="text"
          label="Disabled Field"
          placeholder="Cannot edit"
          disabled
          value="Read-only value"
        />
      </div>

      {/* Required input */}
      <div>
        <h3 className="text-lg font-semibold mb-2">Required Input</h3>
        <Input
          type="text"
          label="Required Field"
          placeholder="This field is required"
          required
        />
      </div>

      {/* Input with custom className */}
      <div>
        <h3 className="text-lg font-semibold mb-2">Custom Styled Input</h3>
        <Input
          type="text"
          label="Custom Style"
          placeholder="With custom classes"
          className="bg-gray-50"
        />
      </div>
    </div>
  );
}

/**
 * Form Example with Multiple Inputs
 */
export function FormExample() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    age: '',
    password: '',
  });

  const [errors, setErrors] = useState({
    name: '',
    email: '',
    age: '',
    password: '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate form
    const newErrors = {
      name: formData.name ? '' : 'Name is required',
      email: formData.email ? '' : 'Email is required',
      age: formData.age ? '' : 'Age is required',
      password: formData.password.length >= 8 ? '' : 'Password must be at least 8 characters',
    };

    setErrors(newErrors);

    // Check if form is valid
    const isValid = Object.values(newErrors).every(error => !error);
    if (isValid) {
      console.log('Form submitted:', formData);
      alert('Form submitted successfully!');
    }
  };

  return (
    <div className="p-6 max-w-md">
      <h2 className="text-2xl font-bold mb-4">Registration Form</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          type="text"
          label="Full Name"
          placeholder="Enter your full name"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          error={errors.name}
          required
        />

        <Input
          type="email"
          label="Email Address"
          placeholder="user@example.com"
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          error={errors.email}
          required
        />

        <Input
          type="number"
          label="Age"
          placeholder="Enter your age"
          value={formData.age}
          onChange={(e) => setFormData({ ...formData, age: e.target.value })}
          error={errors.age}
          min={18}
          max={120}
          required
        />

        <Input
          type="password"
          label="Password"
          placeholder="At least 8 characters"
          value={formData.password}
          onChange={(e) => setFormData({ ...formData, password: e.target.value })}
          error={errors.password}
          required
        />

        <button
          type="submit"
          className="w-full bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 transition"
        >
          Register
        </button>
      </form>
    </div>
  );
}

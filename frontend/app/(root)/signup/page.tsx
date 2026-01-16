"use client"

import { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { api } from "@/lib/api";
import styles from './signup.module.css';

const SignupPage = () => {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: '',
        confirmPassword: '',
        gender: '',
        dateOfBirth: '',
        profileImage: null as File | null,
        agreeToTerms: false
    });

    const [fieldErrors, setFieldErrors] = useState({
        name: '',
        email: '',
        password: '',
        confirmPassword: '',
        gender: '',
        dateOfBirth: '',
        profileImage: '',
        agreeToTerms: ''
    });

    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [passwordStrength, setPasswordStrength] = useState('');
    const [successMessage, setSuccessMessage] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [imagePreview, setImagePreview] = useState<string | null>(null);

    // Calculate password strength
    const calculatePasswordStrength = (password: string) => {
        if (password.length === 0) return '';
        if (password.length < 6) return 'weak';

        let strength = 0;
        if (password.length >= 8) strength++;
        if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
        if (/\d/.test(password)) strength++;
        if (/[^a-zA-Z0-9]/.test(password)) strength++;

        if (strength <= 1) return 'weak';
        if (strength <= 2) return 'medium';
        return 'strong';
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value, type, checked } = e.target;

        setFormData({
            ...formData,
            [name]: type === 'checkbox' ? checked : value
        });

        // Calculate password strength
        if (name === 'password') {
            setPasswordStrength(calculatePasswordStrength(value));
        }

        // Clear field error when user starts typing
        if (fieldErrors[name as keyof typeof fieldErrors]) {
            setFieldErrors({
                ...fieldErrors,
                [name]: ''
            });
        }
    };

    const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];

        if (file) {
            // Validate file size (max 5MB)
            if (file.size > 5 * 1024 * 1024) {
                setFieldErrors({
                    ...fieldErrors,
                    profileImage: 'Image size must be less than 5MB'
                });
                return;
            }

            // Validate file type
            if (!file.type.startsWith('image/')) {
                setFieldErrors({
                    ...fieldErrors,
                    profileImage: 'Please upload a valid image file'
                });
                return;
            }

            setFormData({
                ...formData,
                profileImage: file
            });

            // Create preview
            const reader = new FileReader();
            reader.onloadend = () => {
                setImagePreview(reader.result as string);
            };
            reader.readAsDataURL(file);

            // Clear error
            setFieldErrors({
                ...fieldErrors,
                profileImage: ''
            });
        }
    };

    const handleRemoveImage = () => {
        setFormData({
            ...formData,
            profileImage: null
        });
        setImagePreview(null);
    };

    const validateForm = () => {
        const errors = {
            name: '',
            email: '',
            password: '',
            confirmPassword: '',
            gender: '',
            dateOfBirth: '',
            profileImage: '',
            agreeToTerms: ''
        };

        let isValid = true;

        // Name validation
        if (!formData.name.trim()) {
            errors.name = 'Name is required';
            isValid = false;
        } else if (formData.name.trim().length < 2) {
            errors.name = 'Name must be at least 2 characters';
            isValid = false;
        }

        // Email validation
        if (!formData.email.trim()) {
            errors.email = 'Email is required';
            isValid = false;
        } else {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(formData.email)) {
                errors.email = 'Please enter a valid email address';
                isValid = false;
            }
        }

        // Password validation
        if (!formData.password) {
            errors.password = 'Password is required';
            isValid = false;
        } else if (formData.password.length < 8) {
            errors.password = 'Password must be at least 8 characters';
            isValid = false;
        } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.password)) {
            errors.password = 'Password must contain uppercase, lowercase, and number';
            isValid = false;
        }

        // Confirm password validation
        if (!formData.confirmPassword) {
            errors.confirmPassword = 'Please confirm your password';
            isValid = false;
        } else if (formData.password !== formData.confirmPassword) {
            errors.confirmPassword = 'Passwords do not match';
            isValid = false;
        }

        // Gender validation
        if (!formData.gender) {
            errors.gender = 'Please select your gender';
            isValid = false;
        }

        // Date of birth validation
        if (!formData.dateOfBirth) {
            errors.dateOfBirth = 'Date of birth is required';
            isValid = false;
        } else {
            const birthDate = new Date(formData.dateOfBirth);
            const today = new Date();
            const age = today.getFullYear() - birthDate.getFullYear();

            if (age < 18) {
                errors.dateOfBirth = 'You must be at least 18 years old';
                isValid = false;
            } else if (age > 120) {
                errors.dateOfBirth = 'Please enter a valid date of birth';
                isValid = false;
            }
        }

        // Terms validation
        if (!formData.agreeToTerms) {
            errors.agreeToTerms = 'You must agree to the terms and conditions';
            isValid = false;
        }

        setFieldErrors(errors);
        return isValid;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        setSuccessMessage('');

        if (!validateForm()) {
            return;
        }

        setIsSubmitting(true);

        try {
            // Create FormData for file upload
            const formDataToSend = new FormData();
            formDataToSend.append('name', formData.name);
            formDataToSend.append('email', formData.email);
            formDataToSend.append('password', formData.password);
            formDataToSend.append('gender', formData.gender);
            formDataToSend.append('date_of_birth', formData.dateOfBirth);

            if (formData.profileImage) {
                formDataToSend.append('profile_image', formData.profileImage);
            }

            // Replace with your API endpoint
            await api.post('/api/auth/signup/', formDataToSend, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            setSuccessMessage('Account created successfully! Redirecting to login...');
            setFormData({
                name: '',
                email: '',
                password: '',
                confirmPassword: '',
                gender: '',
                dateOfBirth: '',
                profileImage: null,
                agreeToTerms: false
            });
            setPasswordStrength('');
            setImagePreview(null);

            // Redirect after 2 seconds
            setTimeout(() => {
                window.location.href = '/login';
            }, 2000);

        } catch (err: any) {
            setFieldErrors({
                ...fieldErrors,
                email: err.response?.data?.message || 'Failed to create account. Please try again.'
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className={styles.signup_page}>
            <div className={styles.signup_container}>
                <div className={styles.signup_card}>
                    {/* Header */}
                    <div className={styles.signup_header}>
                        <Image
                            src="/icon.png"
                            alt="Stock Vault"
                            width={70}
                            height={70}
                            className={styles.signup_logo}
                        />
                        <h1 className={styles.signup_title}>Create Account</h1>
                        <p className={styles.signup_subtitle}>
                            Start tracking your investments today
                        </p>
                    </div>

                    {/* Success Message */}
                    {successMessage && (
                        <div className={styles.success_message}>
                            {successMessage}
                        </div>
                    )}

                    {/* Signup Form */}
                    <form onSubmit={handleSubmit} noValidate>
                        {/* Name Field */}
                        <div className={styles.form_group}>
                            <label htmlFor="name">Full Name</label>
                            <input
                                type="text"
                                id="name"
                                name="name"
                                value={formData.name}
                                onChange={handleChange}
                                placeholder="John Doe"
                                className={fieldErrors.name ? styles.error : ''}
                            />
                            {fieldErrors.name && (
                                <span className={styles.field_error}>{fieldErrors.name}</span>
                            )}
                        </div>

                        {/* Email Field */}
                        <div className={styles.form_group}>
                            <label htmlFor="email">Email Address</label>
                            <input
                                type="email"
                                id="email"
                                name="email"
                                value={formData.email}
                                onChange={handleChange}
                                placeholder="john@example.com"
                                className={fieldErrors.email ? styles.error : ''}
                            />
                            {fieldErrors.email && (
                                <span className={styles.field_error}>{fieldErrors.email}</span>
                            )}
                        </div>

                        {/* Gender Field */}
                        <div className={styles.gender_group}>
                            <label>Gender</label>
                            <div className={styles.gender_options}>
                                <div className={styles.gender_option}>
                                    <input
                                        type="radio"
                                        id="male"
                                        name="gender"
                                        value="male"
                                        checked={formData.gender === 'male'}
                                        onChange={handleChange}
                                    />
                                    <label htmlFor="male" className={styles.gender_label}>
                                        <i className="fas fa-mars"></i>
                                        Male
                                    </label>
                                </div>
                                <div className={styles.gender_option}>
                                    <input
                                        type="radio"
                                        id="female"
                                        name="gender"
                                        value="female"
                                        checked={formData.gender === 'female'}
                                        onChange={handleChange}
                                    />
                                    <label htmlFor="female" className={styles.gender_label}>
                                        <i className="fas fa-venus"></i>
                                        Female
                                    </label>
                                </div>
                                <div className={styles.gender_option}>
                                    <input
                                        type="radio"
                                        id="other"
                                        name="gender"
                                        value="other"
                                        checked={formData.gender === 'other'}
                                        onChange={handleChange}
                                    />
                                    <label htmlFor="other" className={styles.gender_label}>
                                        <i className="fas fa-genderless"></i>
                                        Other
                                    </label>
                                </div>
                            </div>
                            {fieldErrors.gender && (
                                <span className={styles.field_error}>{fieldErrors.gender}</span>
                            )}
                        </div>

                        {/* Date of Birth Field */}
                        <div className={styles.form_group}>
                            <label htmlFor="dateOfBirth">Date of Birth</label>
                            <input
                                type="date"
                                id="dateOfBirth"
                                name="dateOfBirth"
                                value={formData.dateOfBirth}
                                onChange={handleChange}
                                max={new Date().toISOString().split('T')[0]}
                                className={fieldErrors.dateOfBirth ? styles.error : ''}
                            />
                            {fieldErrors.dateOfBirth && (
                                <span className={styles.field_error}>{fieldErrors.dateOfBirth}</span>
                            )}
                        </div>

                        {/* Profile Image Upload */}
                        <div className={styles.image_upload_group}>
                            <label>Profile Image (Optional)</label>
                            <div className={styles.image_upload_wrapper}>
                                <div className={styles.image_preview}>
                                    {imagePreview ? (
                                        <img src={imagePreview} alt="Profile preview" />
                                    ) : (
                                        <i className="fas fa-user"></i>
                                    )}
                                </div>
                                <div style={{ flex: 1 }} className={styles.upload_buttons}>
                                    <input
                                        type="file"
                                        id="profileImage"
                                        name="profileImage"
                                        accept="image/*"
                                        onChange={handleImageChange}
                                        className={styles.image_upload_input}
                                    />
                                    <label htmlFor="profileImage" className={styles.image_upload_button}>
                                        <i className="fas fa-upload"></i>&nbsp;Choose Image
                                    </label>
                                    {imagePreview && (
                                        <button
                                            type="button"
                                            onClick={handleRemoveImage}
                                            className={styles.image_remove_button}
                                            style={{ marginLeft: '0.5rem' }}
                                        >
                                            <i className="fas fa-times"></i>&nbsp;Remove
                                        </button>
                                    )}
                                    {fieldErrors.profileImage && (
                                        <span className={styles.field_error}>{fieldErrors.profileImage}</span>
                                    )}
                                </div>
                            </div>
                        </div>

                        {/* Password Field */}
                        <div className={styles.form_group}>
                            <label htmlFor="password">Password</label>
                            <div className={styles.password_wrapper}>
                                <input
                                    type={showPassword ? "text" : "password"}
                                    id="password"
                                    name="password"
                                    value={formData.password}
                                    onChange={handleChange}
                                    placeholder="Enter strong password"
                                    className={fieldErrors.password ? styles.error : ''}
                                />
                                <button
                                    type="button"
                                    className={styles.password_toggle}
                                    onClick={() => setShowPassword(!showPassword)}
                                    aria-label="Toggle password visibility"
                                >
                                    <i className={showPassword ? "fas fa-eye-slash" : "fas fa-eye"}></i>
                                </button>
                            </div>
                            {fieldErrors.password && (
                                <span className={styles.field_error}>{fieldErrors.password}</span>
                            )}
                            {/* Password Strength Indicator */}
                            {formData.password && !fieldErrors.password && (
                                <>
                                    <div className={styles.password_strength}>
                                        <div className={`${styles.password_strength_bar} ${styles[passwordStrength]}`}></div>
                                    </div>
                                    <span className={styles.password_strength_text}>
                                        Password strength: {passwordStrength}
                                    </span>
                                </>
                            )}
                        </div>

                        {/* Confirm Password Field */}
                        <div className={styles.form_group}>
                            <label htmlFor="confirmPassword">Confirm Password</label>
                            <div className={styles.password_wrapper}>
                                <input
                                    type={showConfirmPassword ? "text" : "password"}
                                    id="confirmPassword"
                                    name="confirmPassword"
                                    value={formData.confirmPassword}
                                    onChange={handleChange}
                                    placeholder="Re-enter your password"
                                    className={fieldErrors.confirmPassword ? styles.error : ''}
                                />
                                <button
                                    type="button"
                                    className={styles.password_toggle}
                                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                                    aria-label="Toggle password visibility"
                                >
                                    <i className={showConfirmPassword ? "fas fa-eye-slash" : "fas fa-eye"}></i>
                                </button>
                            </div>
                            {fieldErrors.confirmPassword && (
                                <span className={styles.field_error}>{fieldErrors.confirmPassword}</span>
                            )}
                        </div>

                        {/* Terms Checkbox */}
                        <div className={styles.checkbox_group}>
                            <input
                                type="checkbox"
                                id="agreeToTerms"
                                name="agreeToTerms"
                                checked={formData.agreeToTerms}
                                onChange={handleChange}
                            />
                            <label htmlFor="agreeToTerms">
                                I agree to the <Link href="/terms">Terms of Service</Link> and{' '}
                                <Link href="/privacy">Privacy Policy</Link>
                            </label>
                        </div>
                        {fieldErrors.agreeToTerms && (
                            <span className={styles.field_error} style={{ marginTop: '-1rem', display: 'block', marginBottom: '1rem' }}>
                                {fieldErrors.agreeToTerms}
                            </span>
                        )}

                        {/* Submit Button */}
                        <button
                            type="submit"
                            className={styles.submit_button}
                            disabled={isSubmitting}
                        >
                            {isSubmitting ? 'Creating Account...' : 'Create Account'}
                        </button>
                    </form>

                    {/* Divider */}
                    <div className={styles.divider}>
                        <span>or continue with</span>
                    </div>

                    {/* Social Login Buttons */}
                    <div className={styles.social_buttons}>
                        <button className={styles.social_button}>
                            <i className="fab fa-google"></i>
                            Google
                        </button>
                        <button className={styles.social_button}>
                            <i className="fab fa-github"></i>
                            GitHub
                        </button>
                    </div>

                    {/* Footer */}
                    <div className={styles.signup_footer}>
                        Already have an account?{' '}
                        <Link href="/login">Sign in</Link>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SignupPage;
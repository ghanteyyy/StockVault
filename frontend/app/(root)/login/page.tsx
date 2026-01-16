"use client"

import { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { api } from "@/lib/api";
import styles from './login.module.css';


const LoginPage = () => {
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        rememberMe: false
    });

    const [fieldErrors, setFieldErrors] = useState({
        email: '',
        password: ''
    });

    const [showPassword, setShowPassword] = useState(false);
    const [successMessage, setSuccessMessage] = useState('');
    const [errorMessage, setErrorMessage] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value, type, checked } = e.target;

        setFormData({
            ...formData,
            [name]: type === 'checkbox' ? checked : value
        });

        // Clear field error when user starts typing
        if (fieldErrors[name as keyof typeof fieldErrors]) {
            setFieldErrors({
                ...fieldErrors,
                [name]: ''
            });
        }

        // Clear general error message
        setErrorMessage('');
    };

    const validateForm = () => {
        const errors = {
            email: '',
            password: ''
        };

        let isValid = true;

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
        } else if (formData.password.length < 6) {
            errors.password = 'Password must be at least 6 characters';
            isValid = false;
        }

        setFieldErrors(errors);
        return isValid;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        setSuccessMessage('');
        setErrorMessage('');

        if (!validateForm()) {
            return;
        }

        setIsSubmitting(true);

        try {
            const _email = formData.email;
            const _password = formData.password;

            const response = await api.post('/api/auth/login/', {
                email: formData.email.trim(),
                password: formData.password.trim(),
                rememberMe: formData.rememberMe
            });

            const data = response.data;

            // Store token if provided
            if (response.data.token) {
                localStorage.setItem('token', response.data.token);
            }

            setSuccessMessage('Login successful! Redirecting...');

            // Redirect after 1.5 seconds
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1500);

        } catch (err: any) {
            const message = err.response?.data?.message || 'Invalid email or password. Please try again.';
            setErrorMessage(message);
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleSocialLogin = (provider: string) => {
        // Implement social login logic here
        // Example: window.location.href = `/api/auth/${provider}`;
    };

    return (
        <div className={styles.login_page}>
            <div className={styles.login_container}>
                <div className={styles.login_card}>
                    {/* Header */}
                    <div className={styles.login_header}>
                        <Image
                            src="/icon.png"
                            alt="Stock Vault"
                            width={70}
                            height={70}
                            className={styles.login_logo}
                        />
                        <h1 className={styles.login_title}>Welcome Back</h1>
                        <p className={styles.login_subtitle}>
                            Sign in to continue to your account
                        </p>
                    </div>

                    {/* Success Message */}
                    {successMessage && (
                        <div className={styles.success_message}>
                            {successMessage}
                        </div>
                    )}

                    {/* Error Message */}
                    {errorMessage && (
                        <div className={styles.error_message}>
                            {errorMessage}
                        </div>
                    )}

                    {/* Login Form */}
                    <form onSubmit={handleSubmit} noValidate>
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
                                autoComplete="email"
                            />
                            {fieldErrors.email && (
                                <span className={styles.field_error}>{fieldErrors.email}</span>
                            )}
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
                                    placeholder="Enter your password"
                                    className={fieldErrors.password ? styles.error : ''}
                                    autoComplete="current-password"
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
                        </div>

                        {/* Remember Me & Forgot Password */}
                        <div className={styles.form_options}>
                            <div className={styles.remember_me}>
                                <input
                                    type="checkbox"
                                    id="rememberMe"
                                    name="rememberMe"
                                    checked={formData.rememberMe}
                                    onChange={handleChange}
                                />
                                <label htmlFor="rememberMe">Remember me</label>
                            </div>
                            <Link href="/forgot-password" className={styles.forgot_password}>
                                Forgot password?
                            </Link>
                        </div>

                        {/* Submit Button */}
                        <button
                            type="submit"
                            className={styles.submit_button}
                            disabled={isSubmitting}
                        >
                            {isSubmitting ? 'Signing in...' : 'Sign In'}
                        </button>
                    </form>

                    {/* Divider */}
                    <div className={styles.divider}>
                        <span>or continue with</span>
                    </div>

                    {/* Social Login Buttons */}
                    <div className={styles.social_buttons}>
                        <button
                            className={styles.social_button}
                            onClick={() => handleSocialLogin('google')}
                            type="button"
                        >
                            <i className="fab fa-google"></i>
                            Google
                        </button>
                        <button
                            className={styles.social_button}
                            onClick={() => handleSocialLogin('github')}
                            type="button"
                        >
                            <i className="fab fa-github"></i>
                            GitHub
                        </button>
                    </div>

                    {/* Footer */}
                    <div className={styles.login_footer}>
                        Don't have an account?{' '}
                        <Link href="/signup">Create account</Link>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LoginPage;
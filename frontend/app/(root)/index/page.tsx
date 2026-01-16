"use client"

import LandingEffects from "./LandingEffect";
import Link from 'next/link';
import { useEffect, useState } from 'react';
import {api} from "@/lib/api";
import type { Testinomial, Faqs } from '@/interface/interfaces';
import styles from "./index.module.css";

const IndexPage = () => {
    const [testinomials, setTestinomials] = useState<Testinomial[]>([]);
    const [error, setError] = useState("");

    useEffect(() => {
            api.get('/api/testinomials/')
            .then((res) => setTestinomials(res.data.testinomials))
            .catch((err) => setError(err.response?.data?.message || err.message));
        }, []);


    const [faqs, setFaqs] = useState<Faqs[]>([]);
    const [faqError, setFaqError] = useState();

    useEffect(() => {
        api.get('api/faqs/')
        .then((res) => setFaqs(res.data.faqs))
        .catch((err) => setFaqError(err.response?.data?.message || err.message))
    }, [])

    const [contactForm, setContactForm] = useState({
        name: '',
        email: '',
        subject: '',
        message: ''
    });

    const [fieldErrors, setFieldErrors] = useState({
        name: '',
        email: '',
        message: ''
    });

    const [contactSuccess, setContactSuccess] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleContactChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target;
        setContactForm({
            ...contactForm,
            [name]: value
        });

        if (fieldErrors[name as keyof typeof fieldErrors]) {
            setFieldErrors({
                ...fieldErrors,
                [name]: ''
            });
        }
    };

    const validateForm = () => {
        const errors = {
            name: '',
            email: '',
            message: '',
            subject: ''
        };

        let isValid = true;

        if (!contactForm.name.trim()) {
            errors.name = 'Name is required';
            isValid = false;
        }
        else if (contactForm.name.trim().length < 2) {
            errors.name = 'Name must be at least 2 characters';
            isValid = false;
        }

        if (!contactForm.email.trim()) {
            errors.email = 'Email is required';
            isValid = false;
        }
        if (!contactForm.subject.trim()) {
            errors.subject = 'Subject is required';
            isValid = false;
        }
        else {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(contactForm.email)) {
                errors.email = 'Please enter a valid email address';
                isValid = false;
            }
        }

        if (!contactForm.message.trim()) {
            errors.message = 'Message is required';
            isValid = false;
        }
        else if (contactForm.message.trim().length < 10) {
            errors.message = 'Message must be at least 10 characters';
            isValid = false;
        }

        setFieldErrors(errors);
        return isValid;
    };

    const handleContactSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        setContactSuccess('');

        if (!validateForm()) {
            return;
        }

        setIsSubmitting(true);

        try {
            await api.post('/api/feedback/', contactForm);
            setContactSuccess("Thank you for your message! We'll get back to you soon.");

            setContactForm({ name: '', email: '', subject: '', message: '' });
            setFieldErrors({ name: '', email: '', message: '' });
        }

        catch (err: any) {
            setFieldErrors({
                ...fieldErrors,
                message: err.response?.data?.message || 'Failed to send message. Please try again.'
            });
        }

        finally {
            setIsSubmitting(false);
        }
    };

    return (
        <>
            <LandingEffects />

            <div className={styles.hero_content}>
                <h1>Track. Predict. Profit.</h1>
                <p>Your smart companion for monitoring stock portfolios, analyzing trends, and making better investments.</p>
                <Link href="/signup" className='cta_button'>Get Started</Link>
            </div>

            <section id="features" className={styles.features}>
                <h2>Core Features</h2>
                <div className={styles.feature_cards}>
                    <div className={styles.card}>
                        <i className="fas fa-chart-line"></i>
                        <h3>Live Holdings</h3>
                        <p>Track your investment quantity, price per share, and portfolio health.</p>
                    </div>

                    <div className={styles.card}>
                        <i className="fas fa-star"></i>
                        <h3>Wishlist Management</h3>
                        <p>Add favorite companies and watch their market trends in real-time.</p>
                    </div>

                    <div className={styles.card}>
                        <i className="fas fa-history"></i>
                        <h3>Historical Analytics</h3>
                        <p>View detailed company price history and trends to predict future gains.</p>
                    </div>
                </div>
            </section>

            <section className={styles.why}>
                <h2>Why Choose Stock Vault?</h2>
                <div className={styles.why_grid}>
                    <div>
                        <h3>📊 Data Driven</h3>
                        <p>Make informed decisions based on historical price patterns and trends.</p>
                    </div>

                    <div>
                        <h3>🔒 Secure</h3>
                        <p>Your data is stored securely with modern authentication methods.</p>
                    </div>

                    <div>
                        <h3>⚡ Lightning Fast</h3>
                        <p>Optimized performance ensures smooth experience even on low bandwidth.</p>
                    </div>
                </div>
            </section>

            <section className={styles.how}>
                <h2>How It Works</h2>
                <div className={styles.steps}>
                    <div className={styles.step}>
                        <span>1</span>
                        <h4>Register</h4>
                        <p>Create your free account with email and start tracking.</p>
                    </div>

                    <div className={styles.step}>
                        <span>2</span>
                        <h4>Add Holdings</h4>
                        <p>Enter share quantity, price, and companies you invested in.</p>
                    </div>

                    <div className={styles.step}>
                        <span>3</span>
                        <h4>Analyze</h4>
                        <p>Visualize portfolio health, profit/loss and market movement.</p>
                    </div>
                </div>
            </section>

            <section className={styles.testimonials}>
                <h2>What Users Say</h2>

                {testinomials.map((testinomial) => (
                    <div key={testinomial.message} className={styles.testimony}>
                        <p>{testinomial.message}</p>
                        <strong>{testinomial.user_name}</strong>
                    </div>
                ))}
            </section>

            <section className={styles.faq} id="faq">
                <h2>Frequently Asked Questions</h2>

                <div className={styles.faq_list}>
                    {faqs.map((faq) => (
                        <details key={faq.question} className={styles.details}>
                            <summary className={styles.summary}>{faq.question}</summary>
                            <p>{faq.answer}</p>
                        </details>
                    ))}
                </div>
            </section>

            <section className={styles.about}>
                <h2>About Stock Vault</h2>
                <p>
                    A cutting-edge platform developed as a university final project to help investors stay ahead in Nepal's
                    stock market. Simple, secure, and insightful.
                </p>
            </section>

            <section className={styles.contact} id="contact">
                <h2>Get In Touch</h2>
                <div className={styles.contact_container}>
                    <form method="POST" className={styles.contact_form} onSubmit={handleContactSubmit} noValidate>
                        {contactSuccess && (
                            <div className={styles.success_message}>
                                {contactSuccess}
                            </div>
                        )}

                        <div className={styles.form_group}>
                            <label htmlFor="name">Name <span className={styles.required_field}><span className={styles.required_field}>*</span></span></label>
                            <input
                                type="text"
                                id="name"
                                name="name"
                                value={contactForm.name}
                                onChange={handleContactChange}
                                placeholder="Your full name"
                                className={fieldErrors.name ? styles.error : ''}
                            />
                            {fieldErrors.name && (
                                <span className={styles.error_message}>{fieldErrors.name}</span>
                            )}
                        </div>

                        <div className={styles.form_group}>
                            <label htmlFor="email">Email <span className={styles.required_field}>*</span></label>
                            <input
                                type="email"
                                id="email"
                                name="email"
                                value={contactForm.email}
                                onChange={handleContactChange}
                                placeholder="your.email@example.com"
                                className={fieldErrors.email ? styles.error : ''}
                            />
                            {fieldErrors.email && (
                                <span className={styles.error_message}>{fieldErrors.email}</span>
                            )}
                        </div>

                        <div className={styles.form_group}>
                            <label htmlFor="subject">Subject <span className={styles.required_field}>*</span></label>
                            <input
                                type="text"
                                id="subject"
                                name="subject"
                                value={contactForm.subject}
                                onChange={handleContactChange}
                                placeholder="What is this about?"
                            />

                            {fieldErrors.message && (
                                <span className={styles.error_message}>{fieldErrors.message}</span>
                            )}
                        </div>

                        <div className={styles.form_group}>
                            <label htmlFor="message">Message <span className={styles.required_field}>*</span></label>
                            <textarea
                                id="message"
                                name="message"
                                value={contactForm.message}
                                onChange={handleContactChange}
                                placeholder="Tell us how we can help you..."
                                className={fieldErrors.message ? styles.error : ''}
                            />
                            {fieldErrors.message && (
                                <span className={styles.error_message}>{fieldErrors.message}</span>
                            )}
                        </div>

                        <button
                            type="submit"
                            className={styles.form_button}
                            disabled={isSubmitting}
                        >
                            {isSubmitting ? 'Sending...' : 'Send Message'}
                        </button>
                    </form>
                </div>
            </section>
        </>

    )
}

export default IndexPage;
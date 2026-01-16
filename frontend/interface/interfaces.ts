export interface Testinomial {
    message: string;
    user_name: string;
}

export interface Faqs{
    question: string;
    answer: string;
}

export interface Me {
    id?: number;
    name?: string;
    email?: string;
    profile_image?: string | null;
};
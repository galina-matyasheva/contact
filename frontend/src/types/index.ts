export interface ContactFormData {
  name: string;
  phone: string;
  email: string;
  comment: string;
}

// Used by ContactResponse.ai_analisis
export interface AIAnalysis {
  sentiment: string;
  category: string;
  auto_reply: string;
}

export interface EmailResults {
  owner: boolean;
  user_copy: boolean;
}

export interface ContactResponse {
  success: boolean;
  message: string;
  id: string | null;
  ai_analysis: AIAnalysis | null;
  emails_sent?: EmailResults;
  timestamp?: string;
}

export interface ValidationError {
  field: string;
  message: string;
}

export interface ApiError {
  success: false;
  message: string;
  errors?: ValidationError[];
  status?: number;
}

import re

class ResumeAnalyzer:
    """
    Handles the professional analysis of resumes, providing structured feedback
    on ATS compatibility, skill sets, and career recommendations.
    """
    
    def generate_prompt(self, extracted_text):
        """
        Creates a high-context prompt for the LLM to ensure the output
        is professional and structured using Markdown.
        """
        return f"""
        You are an expert Technical Recruiter and ATS (Applicant Tracking System) Specialist.
        Analyze the following resume text and provide a comprehensive report.
        
        Use the following Markdown structure for the response:
        
        # 📄 RESUME ANALYSIS REPORT
        ---
        ## 📊 ATS Score: [Score]/100
        
        ## ✅ Key Strengths
        * **[Strength 1]**: [Brief Description]
        * **[Strength 2]**: [Brief Description]
        
        ## 🛠️ Technical Competencies
        | Category | Skills Identified |
        | :--- | :--- |
        | Programming | [Languages] |
        | AI/ML | [Frameworks/Tools] |
        | Tools/Cloud | [DevOps/Cloud] |
        
        ## ⚠️ Areas for Improvement
        * [Point 1]
        * [Point 2]
        
        ## 🚀 Career Recommendations
        * [Role 1]
        * [Role 2]
        
        ---
        **Final Verdict:** [One sentence summary]
        
        Resume Content:
        {extracted_text}
        """

    def analyze(self, text, client, model):
        """
        Executes the analysis using the provided LLM client.
        
        Args:
            text (str): The extracted PDF content.
            client: The initialized Groq or Gemini client.
            model (str): The specific model ID (e.g., Llama-3).
        """
        prompt = self.generate_prompt(text)
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3, # Low temperature for factual consistency
        )
        return response.choices[0].message.content.strip()

# Singleton instance to be imported by app.py
resume_expert = ResumeAnalyzer()
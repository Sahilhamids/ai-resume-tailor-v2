export default function About() {
  return (
    <div>
      <div className="card">
        <h3>About This Project</h3>
        <p>
          Career Intelligence Platform is an AI-powered toolkit for job seekers: tailor your resume
          to a specific job description, audit it against ATS scoring with keyword-gap analysis,
          generate a matching cover letter, and track your applications — all without needing to
          create an account first.
        </p>
        <p className="muted">
          The AI is constrained with strict anti-hallucination prompting: it's instructed never to
          invent metrics, employers, or skills that aren't in your actual profile data, and a
          separate deterministic check fact-validates any "missing keyword" claims against your
          real resume text before showing them to you.
        </p>
      </div>

      <div className="card">
        <h3>Developer</h3>
        <p><b>Sahil Shaikh</b></p>
        <p className="muted">
          Built end-to-end: FastAPI + PostgreSQL backend, React frontend, and a Gemini/Groq
          fallback AI pipeline, deployed on Render.
        </p>
        <p>
          <a href="https://github.com/Sahilhamids" target="_blank" rel="noreferrer">GitHub: @Sahilhamids</a>
        </p>
      </div>
    </div>
  );
}

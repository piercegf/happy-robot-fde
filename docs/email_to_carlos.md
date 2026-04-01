# Email to Carlos Becker

**To:** Carlos Becker (c.becker@happyrobot.ai)  
**From:** Alejandro Pérez  
**Subject:** Inbound carrier sales build — live demo & reviewer handoff

---

Hi Carlos,

Ahead of our meeting, here is the **production-ready** package for the Acme Logistics inbound carrier sales build.

**Live operations dashboard** (open in browser — do not use a downloaded HTML file):  
https://happy-robot-fde-production-f148.up.railway.app/dashboard  

**HappyRobot workflow:**  
https://platform.happyrobot.ai/fdealejandroperez/workflows/gchtmr5tol1e  

**Repository** (technical build, deployment notes, business summary):  
https://github.com/piercegf/happy-robot-fde  

**Reviewer handoff** (links, access model, doc index, discussion topics — same content you can forward internally):  
`docs/handoff_carlos.md` in the repo root path above.

**Scope in one line:** Voice agent on HappyRobot with tools to a FastAPI backend on Railway — FMCSA verification (with fallback), fuzzy load match, negotiation to a **95% floor** over up to three rounds, structured post-call outcomes, and a real-time ops dashboard (conversion, revenue capture vs posted rate, sentiment, lanes, peak hours).

You can exercise **voice** from the HappyRobot side as you usually would; you do not need my local-only Vite token stack unless you want to mirror my dev setup (README optional section).

I’d love your perspective in the meeting on **dynamic floors by lane**, **graceful lane pivots mid-call**, **outbound callback follow-up**, and **Spanish** for the carrier base.

Looking forward to walking through it with you.

— Alejandro

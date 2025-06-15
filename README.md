# New-CAPTCHA-System

## 🔍 Background

CAPTCHA (Completely Automated Public Turing test to tell Computers and Humans Apart) systems have long been used as a defense mechanism against automated bots. However, recent advancements in machine learning have made it increasingly easier for AI-powered programs to bypass conventional CAPTCHA mechanisms, including both text-based and image-based CAPTCHAs.

![Previous CAPTCHA Research and Defeat Methods](./assets/captcha_background.png)

As shown in the image above:
- Traditional CAPTCHA systems such as reCAPTCHA v2 and FunCaptcha have been successfully solved using deep learning techniques.
- For example, character-based CAPTCHA has been defeated via segmentation and denoising pipelines, and even reCAPTCHA v2 image challenges can be broken using object detection models like YOLOv8.
- These breakthroughs enable bots to solve CAPTCHA in under 10 seconds at very low costs, posing a significant security threat.

With the increasing sophistication of these automated solvers, a new form of CAPTCHA is required — one that better exploits the **cognitive gap between humans and machines**.

## 🧠 Our Approach

To address this issue, we propose a **Multi-Modal CAPTCHA system** that leverages:
- Visual reasoning
- Human intuition
- Real-time interaction

Instead of asking users to simply click or type, our system requires users to **draw** or **highlight** semantic regions (e.g., cloud shapes, dangerous objects), which introduces complexity that is **trivial for humans but difficult for machines**.

Our goal is to develop a CAPTCHA system that:
- Adapts to various visual prompts
- Is resistant to automation attacks
- Maintains usability and accessibility for real users

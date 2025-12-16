# LLM Package Hallucinations

In this project, we reproduced and extended prior research on package hallucinations in code-generating large language models, focusing on how often models invent non-existent software packages that could pose real security risks. Using smaller, locally hosted models (DeepSeek-Coder 1.3B and TinyLlama), we evaluated hallucination behavior across multiple programming ecosystems and established a baseline using the GARAK vulnerability scanning framework.

We then implemented and tested practical mitigation strategies, including safety instructions and automated package registry verification via a FastAPI wrapper. These guardrails consistently reduced attack success rates across ecosystems, with some languages seeing substantial improvements. Finally, we explored prompt engineering techniques, showing that stronger, repetitive safety-focused prompts were especially effective at lowering hallucination rates.

Overall, our results demonstrate that even small models can pose meaningful security risks, but also that lightweight, external defenses and careful prompt design can significantly improve safety, reinforcing the need to integrate AI security measures throughout the software development lifecycle.

--

## 📊 Results

Attack Success Rates Before and After Mitigation Technques
![ASRGRAPH](Assets/ASR_Graph_Mitigation.png)
![BASELINE](Assets/Baseline_Table.png)
![AFTERGRAPH](Assets/Baseline_After_Mitigation_Table.png)

Prompt Engineering Matrix
![PROMPTMATRIX](Assets/Prompt_Matrix.png)

Prompt Engineering Performance
![PROMPTPERF](Assets/Avg_ASR_Graph_For_Prompt.png)

--

## 🔗 Link to Original Paper
- !["We Have a Package for You! A Comprehensive Analysis of Package Hallucinations by Code Generating LLMs"](https://www.usenix.org/conference/usenixsecurity25/presentation/spracklen)

# Stock Market Prediction using LLM
- So, basically, the LLM will be able to predict the stock market, I want to find that out. 
- The LLM will be predicting the stock market, so what else does it need as context? 
1. News 
- Latest News vs Hot News
- if Hot News: top 1 is enough? top 3/5/10.
2. Company Description (Follows a specific format like `[Company] began operations in [year] with a vision to [vision]. [Name] is the current [CEO/MD/President] of the company.`)
3. Predict only for the next trading session's end performance.
4. Prompting techniques to follow:
- Zero shot prompting
- One shot prompting
- CoT
- ToT
5. Models to compare:
- SUTRA
- GPT-4o
- Grok
- LLAMA
- Google Gemini
6. Output:
- Test with different output types such as JSON, text output, python code output, markdown format. Does each of these cause the output to be different? Make observations.
7. Future directions: 
- Test in different languages


#### For our first experiment:
1. Top 10 from Google News
2. One prompting where news & name will be given nothing more nothing less (no persona) (in normal text format | not md or json format of query)
3. Predict what's going to happen tomorrow.
4. Zero shot prompting
5. SUTRA, GPT-4o, Grok, Gemini
6. JSON output
7. English
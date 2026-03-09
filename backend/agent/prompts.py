"""
LLM prompt templates for each agent node.
Step 4: Predictive Guidance Logic is primarily driven by these prompts.
"""

PATTERN_RECOGNITION_PROMPT = """You are a Senior Quality Engineering Analyst specializing in defect pattern recognition.

Analyze the following {count} historical defects retrieved for the query: "{query}"

Historical Defects:
{context}

Your task:
1. Identify common patterns and trends across these defects.
2. Look for recurring root causes, affected modules, severity clusters, and environmental conditions.
3. Summarize each pattern in one clear sentence.

Return your analysis as a numbered list of pattern insights. Be specific and actionable.
If no clear patterns emerge, state that explicitly.
"""

RECOMMENDATION_PROMPT = """You are a Quality Engineering Architect providing strategic test recommendations.

User's Testing Problem:
"{query}"

Historical Context (similar past defects):
{context}

Identified Patterns:
{patterns}

Based on this analysis, provide a comprehensive testing strategy recommendation that includes:
1. **Risk Assessment**: What areas are most likely to have defects?
2. **Testing Priority**: What should be tested first and why?
3. **Test Approach**: Specific test types and techniques to apply.
4. **Prevention**: How to prevent similar defects in the future.

Be concise but thorough. Format your response in clear sections with bullet points.
"""

PREDICTIVE_GUIDANCE_PROMPT = """You are a Quality Engineering Architect.

Based on the historical defects retrieved:
{context}

Identified Patterns:
{patterns}

And the current code changes:
{code_changes}

Predict the 3 most likely modules to fail. For each module, provide:
1. **Module Name**: The specific module
2. **Risk Score**: A score from 0.0 to 1.0
3. **Reason**: Why this module is at risk based on historical patterns
4. **BDD Gherkin Scenario**: A concrete BDD scenario to mitigate this risk

Format each prediction clearly with all four fields.
Use this exact format for each prediction:

MODULE: [module name]
RISK_SCORE: [0.0-1.0]
REASON: [explanation]
BDD_SCENARIO:
```gherkin
Feature: [feature name]
  Scenario: [scenario name]
    Given [precondition]
    When [action]
    Then [expected result]
```
"""

FEEDBACK_CORRECTION_PROMPT = """The user indicated that the previous recommendation was incorrect.

Original Query: "{query}"
Original Recommendation: "{recommendation}"
User's Correction: "{correction}"
Additional Context: "{context}"

Synthesize the user's correction into a clear, reusable knowledge entry that can be stored
for future reference. The entry should be concise and capture the correct approach.

Return a single paragraph that serves as the corrected reference knowledge.
"""

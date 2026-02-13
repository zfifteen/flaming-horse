"""
Narration script (recovered)
"""

SCRIPT = {
    "intro": """Welcome to this guide on writing great git commit messages. In software development, commit messages are more than just notes—they're documentation that helps teams collaborate, maintain code quality, and understand project history. A clear, concise, and reviewable commit message can save time during code reviews and make debugging much easier down the line.""",
    
    "bad_examples": """Let's start by looking at some common mistakes that make commit messages ineffective. You might see something like 'fix bug'—too vague, no context about what was broken or how it was fixed. Or 'update code'—this tells us nothing specific. Another bad example is 'merge branch'—this is just stating what the tool did, not explaining why or what changed. These kinds of messages leave reviewers guessing and make it hard to track changes over time.""",
    
    "good_practices": """Now, let's talk about what makes a commit message great. Start with a clear, imperative subject line under 50 characters, like 'Fix authentication timeout bug' or 'Add user validation to login form'. Follow it with a more detailed body explaining what changed and why, using bullet points if needed. Keep it concise but informative—aim for the body to be readable in one glance. Always write in present tense, as if you're giving a command to the codebase.""",
    
    "tools_techniques": """To make writing good commit messages easier, try these practical tips. Use git commit with the -m flag for simple changes, or omit -m to open your editor for longer messages. Tools like commitizen can guide you with structured prompts, while git hooks can enforce message standards. For complex changes, reference issue numbers like 'Fix #123: handle null user case'. And remember, review your message before committing—read it back and ask if it would help a future developer understand the change.""",
    
    "recap": """To recap the key principles for writing great git commit messages: keep them clear by being specific about what changed, concise by avoiding unnecessary details, and reviewable by providing enough context for code reviewers. Start with an imperative subject line, add a body when needed, and always consider your future self or teammates who might need to understand this change. Good commit messages are an investment in your project's maintainability.""",
}

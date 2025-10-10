from aws.bedrock_client import call_claude

res = call_claude("What does the Indian Supreme Court say about the Right to Privacy?")
print(res)
# Manual Instructions for Checking GitHub Actions Workflow

Since we can't directly check the GitHub Actions workflow status from the terminal, here are the manual instructions for checking the workflow status:

## Steps to Check GitHub Actions Workflow

1. Open the GitHub repository [minarovic/AI-agent-PoC3](https://github.com/minarovic/AI-agent-PoC3) in your web browser

2. Click on the "Actions" tab at the top of the repository page

3. You should see a list of workflow runs. Look for the latest workflow run that corresponds to the commit we just pushed: "Finalizace dokumentace a konfigurace pro nasazení na LangGraph Platform"

4. Click on the workflow run to see the details

5. Monitor the progress of the workflow run. It should include the following jobs:
   - test
   - deploy-dev

6. If the workflow completes successfully, you'll see green checkmarks next to each job

7. Once completed, find the "Artifacts" section at the bottom of the workflow run page

8. Download the "langgraph-package" artifact, which contains the files needed for manual deployment to LangGraph Platform

## Next Steps After Download

1. Unzip the downloaded artifact

2. Follow the manual deployment instructions in `doc/manual_langgraph_deployment.md`

3. Verify the deployment by testing the API endpoint as described in the documentation

import { LinearClient } from "@linear/sdk";
import * as core from '@actions/core';

async function run() {
  try {
    const labelName = core.getInput('label_name');
    const linearId = core.getInput('linear_issue_id');
    const linearApiKey = core.getInput('linear_api_key');

    const linearClient = new LinearClient({
      apiKey: linearApiKey,
    });

    const issue = await linearClient.issue(linearId);
    if (!issue) {
      throw new Error(`Issue with ID ${linearId} not found`);
    }

    // Get current labels
    const currentLabels = await issue.labels();
    const currentLabelNames = currentLabels.nodes.map(l => l.name.toLowerCase());

    // Check if label already exists
    if (currentLabelNames.includes(labelName.toLowerCase())) {
      core.info(`Label "${labelName}" is already added to issue ${linearId}`);
      return;
    }

    const labels = await linearClient.issueLabels();
    const label = labels.nodes.find(l => l.name.toLowerCase() === labelName.toLowerCase());
    if (!label) {
      throw new Error(`Label "${labelName}" not found`);
    }

    await linearClient.updateIssue(linearId, {
      labelIds: [...currentLabels.nodes.map(l => l.id), label.id],
    });

    core.info(`Successfully added label "${labelName}" to issue ${linearId}`);
  } catch (error: any) {
    core.setFailed(error.message);
  }
}

run(); 
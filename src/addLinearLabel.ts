import { LinearClient } from "@linear/sdk";
import * as dotenv from "dotenv";

dotenv.config();

interface AddLabelParams {
  labelName: string;
  linearId: string;
  linearApiKey: string;
}

export async function addLinearLabel({ labelName, linearId, linearApiKey }: AddLabelParams): Promise<void> {
  try {
    // Initialize Linear client
    const linearClient = new LinearClient({
      apiKey: linearApiKey,
    });

    // Get the issue
    const issue = await linearClient.issue(linearId);
    if (!issue) {
      throw new Error(`Issue with ID ${linearId} not found`);
    }

    // Get all labels
    const labels = await linearClient.issueLabels();
    
    // Find the label by name
    const label = labels.nodes.find(l => l.name.toLowerCase() === labelName.toLowerCase());
    if (!label) {
      throw new Error(`Label "${labelName}" not found`);
    }

    // Add the label to the issue
    await linearClient.updateIssue(linearId, {
      labelIds: [...(await issue.labels()).nodes.map(l => l.id), label.id],
    });

    console.log(`Successfully added label "${labelName}" to issue ${linearId}`);
  } catch (error) {
    console.error("Error adding label to Linear issue:", error);
    throw error;
  }
}

// Example usage
if (require.main === module) {
  const labelName = process.argv[2];
  const linearId = process.argv[3];
  const linearApiKey = process.env.LINEAR_API_KEY;

  if (!labelName || !linearId || !linearApiKey) {
    console.error("Usage: node addLinearLabel.js <labelName> <linearId>");
    console.error("Make sure LINEAR_API_KEY is set in your environment variables");
    process.exit(1);
  }

  addLinearLabel({
    labelName,
    linearId,
    linearApiKey,
  }).catch(console.error);
} 
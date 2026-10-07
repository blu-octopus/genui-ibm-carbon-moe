import { Heading, InlineNotification, Modal, ModalBody, Stack, TextInput } from '@carbon/react';
import '@carbon/styles/css/styles.css';

export default function Prompt05DestructiveModal() {
  return (
    <Modal open danger modalHeading="Delete workspace?" modalLabel="Destructive action" ariaLabel="Confirm workspace deletion" primaryButtonText="Delete" secondaryButtonText="Cancel" preventCloseOnClickOutside shouldSubmitOnEnter={false}>
      <ModalBody>
        <Stack gap=5>
          <InlineNotification kind="warning" title="This cannot be undone" subtitle="All projects, members, and audit logs in this workspace will be permanently removed." lowContrast hideCloseButton />
          <p className="cds--type-body-01">Type the workspace name to confirm you understand this action.</p>
          <TextInput id="confirm-name" labelText="Workspace name" placeholder="production-workspace" invalid={false} invalidText="Name does not match" />
        </Stack>
      </ModalBody>
    </Modal>
  );
}

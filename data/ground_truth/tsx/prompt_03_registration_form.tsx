import { Button, Column, Form, FormGroup, Grid, Heading, ProgressIndicator, ProgressStep, Stack, TextInput, Tooltip } from '@carbon/react';
import '@carbon/styles/css/styles.css';

export default function Prompt03RegistrationForm() {
  return (
    <Grid fullWidth={false} ariaLabel="User registration">
      <Column sm=4 md=6 lg=8>
        <Stack gap=6>
          <p className="cds--type-heading-03">Create account</p>
          <ProgressIndicator currentIndex=0 spaceEqually ariaLabel="Registration steps">
            <ProgressStep label="Profile" description="Name and email" complete={false} current />
            <ProgressStep label="Security" description="Password" complete={false} current={false} />
            <ProgressStep label="Confirm" description="Review details" complete={false} current={false} />
          </ProgressIndicator>
          <Form ariaLabel="Registration profile step">
            <FormGroup legendText="Profile">
              <TextInput id="full-name" labelText="Full name" placeholder="Ada Lovelace" invalid={false} invalidText="Enter your full name" helperText="As shown on your ID" />
              <TextInput id="email" labelText="Email" placeholder="ada@example.com" invalid={false} invalidText="Enter a valid email" helperText="We will send a verification link" />
              <Tooltip label="Why we need this" description="Email is used for account recovery and security alerts." />
            </FormGroup>
            <Stack gap=4 orientation="horizontal">
              <Button kind="secondary" disabled>Back</Button>
              <Button kind="primary">Continue</Button>
            </Stack>
          </Form>
        </Stack>
      </Column>
    </Grid>
  );
}

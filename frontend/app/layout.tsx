import '@carbon/styles/css/styles.css';
import type { ReactNode } from 'react';

export const metadata = {
  title: 'Carbon MoE Test Bench',
  description: 'IBM Carbon renderer for genui-ibm-carbon-moe',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

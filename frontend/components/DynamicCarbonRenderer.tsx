import type { ElementType } from 'react';
import type { CarbonNode } from './types';
import {
  Button,
  Column,
  DataTable,
  DatePicker,
  DatePickerInput,
  Dropdown,
  Form,
  FormGroup,
  Grid,
  Heading,
  InlineNotification,
  Modal,
  Pagination,
  ProgressIndicator,
  ProgressStep,
  Search,
  Stack,
  Tag,
  TextInput,
  Tile,
  Tooltip,
} from '@carbon/react';

const MAP: Record<string, ElementType> = {
  Grid,
  Column,
  Stack,
  Button,
  TextInput,
  Dropdown,
  DatePicker,
  DatePickerInput,
  Tag,
  Tile,
  Search,
  Form,
  FormGroup,
  ProgressIndicator,
  ProgressStep,
  Pagination,
  Modal,
  InlineNotification,
  Tooltip,
  Heading,
  DataTable,
};

function headingClass(token?: string): string {
  if (!token) return '';
  return `cds--type-${token.replace('$', '').replace(/_/g, '-')}`;
}

export function DynamicCarbonRenderer({ node }: { node: CarbonNode }) {
  if (!node) return null;

  if (node.type === 'Heading') {
    return (
      <p className={headingClass(node.props?.token as string | undefined)}>
        {String(node.props?.text ?? '')}
      </p>
    );
  }

  if (node.type === 'Button') {
    const { text, ...rest } = node.props || {};
    return <Button {...rest}>{String(text ?? 'Button')}</Button>;
  }

  if (node.type === 'Tag') {
    const { text, ...rest } = node.props || {};
    return <Tag {...rest}>{String(text ?? '')}</Tag>;
  }

  if (node.type === 'DataTable') {
    const headers = (node.props?.headers as { key: string; header: string }[]) || [];
    const rows = (node.props?.rows as Record<string, string>[]) || [];
    return (
      <DataTable rows={rows} headers={headers} aria-label={String(node.props?.ariaLabel ?? 'Data table')}>
        {({ rows: r, headers: h, getTableProps, getHeaderProps, getRowProps }) => (
          <table {...getTableProps()}>
            <thead>
              <tr>
                {h.map((header) => (
                  <th {...getHeaderProps({ header })} key={header.key}>
                    {header.header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {r.map((row) => (
                <tr {...getRowProps({ row })} key={row.id}>
                  {row.cells.map((cell) => (
                    <td key={cell.id}>{cell.value}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </DataTable>
    );
  }

  if (node.type === 'Modal') {
    const rest = { ...(node.props || {}) };
    return (
      <Modal open {...rest}>
        {(node.children || []).map((child, i) => (
          <DynamicCarbonRenderer key={i} node={child} />
        ))}
      </Modal>
    );
  }

  if (node.type === 'ModalBody') {
    return (
      <div>
        {(node.children || []).map((child, i) => (
          <DynamicCarbonRenderer key={i} node={child} />
        ))}
      </div>
    );
  }

  if (node.type === 'Tooltip') {
    return (
      <Tooltip label={String(node.props?.label ?? 'Info')}>
        <button type="button" className="cds--tooltip-trigger">
          ?
        </button>
      </Tooltip>
    );
  }

  const Cmp = MAP[node.type];
  if (!Cmp) {
    return (
      <div data-unknown-carbon-type={node.type}>
        {(node.children || []).map((child, i) => (
          <DynamicCarbonRenderer key={i} node={child} />
        ))}
      </div>
    );
  }

  const props = { ...(node.props || {}) };
  delete props.text;

  return (
    <Cmp {...props}>
      {(node.children || []).map((child, i) => (
        <DynamicCarbonRenderer key={i} node={child} />
      ))}
    </Cmp>
  );
}

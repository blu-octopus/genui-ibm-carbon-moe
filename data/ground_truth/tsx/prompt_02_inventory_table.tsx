import { Column, DataTable, Grid, Heading, Pagination, Stack } from '@carbon/react';
import '@carbon/styles/css/styles.css';

export default function Prompt02InventoryTable() {
  return (
    <Grid fullWidth ariaLabel="Inventory management">
      <Column sm=4 md=8 lg=16>
        <Stack gap=5>
          <p className="cds--type-heading-03">Inventory</p>
          <DataTable ariaLabel="Inventory table with batch actions" useZebraStyles headers={[{"key": "sku", "header": "SKU"}, {"key": "name", "header": "Item"}, {"key": "qty", "header": "Qty"}, {"key": "status", "header": "Status"}]} rows={[{"id": "i1", "sku": "SKU-100", "name": "Sensor Kit", "qty": "42", "status": "In stock"}, {"id": "i2", "sku": "SKU-220", "name": "Cable Pack", "qty": "8", "status": "Low"}, {"id": "i3", "sku": "SKU-318", "name": "Mount Plate", "qty": "0", "status": "Backorder"}]} batchActions={[{"label": "Export", "kind": "primary"}, {"label": "Archive", "kind": "danger--ghost"}]} rowTags={{"i1": {"type": "green", "text": "In stock"}, "i2": {"type": "warm-gray", "text": "Low"}, "i3": {"type": "red", "text": "Backorder"}}} />
          <Pagination page=1 pageSize=10 totalItems=3 pageSizes={[10, 20, 50]} ariaLabel="Inventory pagination" />
        </Stack>
      </Column>
    </Grid>
  );
}

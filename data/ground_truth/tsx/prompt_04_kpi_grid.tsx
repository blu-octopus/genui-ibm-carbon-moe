import { Column, Dropdown, Grid, Heading, Stack, Tag, Tile } from '@carbon/react';
import '@carbon/styles/css/styles.css';

export default function Prompt04KpiGrid() {
  return (
    <Grid fullWidth ariaLabel="Executive KPI overview">
      <Column sm=4 md=8 lg=16>
        <Stack gap=5>
          <Stack gap=4 orientation="horizontal">
            <p className="cds--type-heading-03">Executive KPIs</p>
            <Dropdown id="kpi-range" titleText="Time range" label="Last 30 days" items={["Last 7 days", "Last 30 days", "Quarter to date"]} ariaLabel="Filter KPI time range" />
          </Stack>
          <Grid narrow>
            <Column sm=4 md=4 lg=4>
              <Tile ariaLabel="Revenue KPI">
                <Stack gap=3>
                  <p className="cds--type-label-01">Revenue</p>
                  <p className="cds--type-heading-05">$2.4M</p>
                  <Tag type="green" ariaLabel="Revenue up twelve percent">▲ 12%</Tag>
                </Stack>
              </Tile>
            </Column>
            <Column sm=4 md=4 lg=4>
              <Tile ariaLabel="Active users KPI">
                <Stack gap=3>
                  <p className="cds--type-label-01">Active users</p>
                  <p className="cds--type-heading-05">18.2k</p>
                  <Tag type="blue" ariaLabel="Active users up four percent">▲ 4%</Tag>
                </Stack>
              </Tile>
            </Column>
            <Column sm=4 md=4 lg=4>
              <Tile ariaLabel="Conversion KPI">
                <Stack gap=3>
                  <p className="cds--type-label-01">Conversion</p>
                  <p className="cds--type-heading-05">3.1%</p>
                  <Tag type="red" ariaLabel="Conversion down one percent">▼ 1%</Tag>
                </Stack>
              </Tile>
            </Column>
            <Column sm=4 md=4 lg=4>
              <Tile ariaLabel="NPS KPI">
                <Stack gap=3>
                  <p className="cds--type-label-01">NPS</p>
                  <p className="cds--type-heading-05">62</p>
                  <Tag type="teal" ariaLabel="NPS stable">Stable</Tag>
                </Stack>
              </Tile>
            </Column>
          </Grid>
        </Stack>
      </Column>
    </Grid>
  );
}

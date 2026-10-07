import { Column, DataTable, DatePicker, DatePickerInput, Grid, Heading, Search, Stack, Tag, Tile } from '@carbon/react';
import '@carbon/styles/css/styles.css';

export default function Prompt01TravelDashboard() {
  return (
    <Grid fullWidth ariaLabel="Travel comparison dashboard">
      <Column sm=4 md=8 lg=16>
        <Stack gap=7>
          <p className="cds--type-heading-03">Travel comparison</p>
          <DatePicker datePickerType="range" ariaLabel="Travel date range">
            <DatePickerInput id="travel-start" labelText="Departure" placeholder="mm/dd/yyyy" />
            <DatePickerInput id="travel-end" labelText="Return" placeholder="mm/dd/yyyy" />
          </DatePicker>
          <Grid narrow>
            <Column sm=4 md=4 lg=5>
              <Tile ariaLabel="Average price metric">
                <Stack gap=3>
                  <p className="cds--type-label-01">Avg price</p>
                  <p className="cds--type-heading-04">$412</p>
                  <Tag type="green">Down 8%</Tag>
                </Stack>
              </Tile>
            </Column>
            <Column sm=4 md=4 lg=5>
              <Tile ariaLabel="Average duration metric">
                <Stack gap=3>
                  <p className="cds--type-label-01">Avg duration</p>
                  <p className="cds--type-heading-04">6h 20m</p>
                  <Tag type="blue">Direct preferred</Tag>
                </Stack>
              </Tile>
            </Column>
            <Column sm=4 md=8 lg=6>
              <Tile ariaLabel="Options counted metric">
                <Stack gap=3>
                  <p className="cds--type-label-01">Options</p>
                  <p className="cds--type-heading-04">24</p>
                  <Tag type="gray">Filtered</Tag>
                </Stack>
              </Tile>
            </Column>
          </Grid>
          <Search id="flight-filter" labelText="Filter flights" placeholder="Filter by airline or airport" size="md" />
          <DataTable ariaLabel="Flight options table" headers={[{"key": "airline", "header": "Airline"}, {"key": "route", "header": "Route"}, {"key": "duration", "header": "Duration"}, {"key": "price", "header": "Price"}]} rows={[{"id": "f1", "airline": "Example Air", "route": "SFO \u2192 JFK", "duration": "5h 45m", "price": "$389"}, {"id": "f2", "airline": "Sample Jets", "route": "SFO \u2192 JFK", "duration": "6h 10m", "price": "$420"}]} />
        </Stack>
      </Column>
    </Grid>
  );
}

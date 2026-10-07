import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET(
  _req: NextRequest,
  context: { params: { id: string } },
) {
  const id = context.params.id;
  const filePath = path.join(process.cwd(), '..', 'data', 'ground_truth', `${id}.json`);
  if (!fs.existsSync(filePath)) {
    return NextResponse.json({ error: 'not found', id }, { status: 404 });
  }
  const raw = fs.readFileSync(filePath, 'utf8');
  return NextResponse.json(JSON.parse(raw));
}

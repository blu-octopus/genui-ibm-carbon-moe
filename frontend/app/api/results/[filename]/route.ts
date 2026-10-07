import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET(
  _req: NextRequest,
  context: { params: { filename: string } },
) {
  const filename = context.params.filename;
  if (!filename || filename.includes('..') || filename.includes('/') || filename.includes('\\')) {
    return NextResponse.json({ error: 'invalid filename' }, { status: 400 });
  }
  if (!filename.endsWith('.json')) {
    return NextResponse.json({ error: 'must be .json' }, { status: 400 });
  }
  const filePath = path.join(process.cwd(), '..', 'data', 'results', filename);
  if (!fs.existsSync(filePath)) {
    return NextResponse.json({ error: 'not found', filename }, { status: 404 });
  }
  const payload = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  const document = payload.document ?? null;
  return NextResponse.json({
    filename,
    system: payload.system ?? null,
    model: payload.model ?? null,
    prompt_id: payload.prompt_id ?? null,
    document,
  });
}

import fs from 'fs/promises';
import path from 'path';

const DATA_DIR = path.resolve(process.cwd(), '../defect');

export interface DatasetFile {
  name: string;
  path: string;
  size: number;
}

export async function listDatasets(): Promise<DatasetFile[]> {
  try {
    const files = await fs.readdir(DATA_DIR);
    const datasets: DatasetFile[] = [];

    for (const file of files) {
      if (file.endsWith('.json')) {
        const filePath = path.join(DATA_DIR, file);
        const stats = await fs.stat(filePath);
        datasets.push({
          name: file,
          path: filePath,
          size: stats.size,
        });
      }
    }
    return datasets;
  } catch (error) {
    console.error('Error listing datasets:', error);
    return [];
  }
}

export async function readDatasetSample(fileName: string, sampleSize = 5): Promise<any> {
  try {
    const filePath = path.join(DATA_DIR, fileName);
    // Validate path to prevent directory traversal
    if (!filePath.startsWith(DATA_DIR)) {
      throw new Error('Invalid file path');
    }

    const content = await fs.readFile(filePath, 'utf-8');
    const data = JSON.parse(content);

    if (Array.isArray(data)) {
      return {
        type: 'array',
        length: data.length,
        sample: data.slice(0, sampleSize),
        keys: data.length > 0 ? Object.keys(data[0]) : [],
      };
    } else if (typeof data === 'object') {
      // If it's a dict/object, show keys and maybe a sample of values
        // Try to find list-like values to sample
        const keys = Object.keys(data);
        const sample: any = {};
        for(const k of keys) {
            if(Array.isArray(data[k])) {
                 sample[k] = `Array(${data[k].length}) - Sample: ${JSON.stringify(data[k].slice(0,2))}`
            } else {
                 sample[k] = typeof data[k] === 'object' ? 'Object' : data[k];
            }
        }
      return {
        type: 'object',
        keys,
        sample
      };
    }
    return { type: 'unknown', data: content.slice(0, 500) };
  } catch (error) {
    console.error('Error reading dataset:', error);
    return null;
  }
}

export async function getDatasetContent(fileName: string): Promise<any> {
     try {
    const filePath = path.join(DATA_DIR, fileName);
    // Validate path to prevent directory traversal
    if (!filePath.startsWith(DATA_DIR)) {
      throw new Error('Invalid file path');
    }

    const content = await fs.readFile(filePath, 'utf-8');
    return JSON.parse(content);
  } catch (error) {
    console.error('Error reading dataset full content:', error);
    return null;
  }
}

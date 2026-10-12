import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = { title: 'PromiseTrap — Every promise deserves evidence.', description: 'A multimodal evidence investigation workspace powered by Gemma 4 and PromiseGraph.' };
export default function RootLayout({children}: Readonly<{children: React.ReactNode}>) { return <html lang="en"><body>{children}</body></html>; }

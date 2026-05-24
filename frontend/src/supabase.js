import { createClient } from "@supabase/supabase-js";

const supabaseUrl = "https://ddjehwuxistyrqkbgwnd.supabase.co";

const supabaseKey =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRkamVod3V4aXN0eXJxa2Jnd25kIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg1MDA0NjYsImV4cCI6MjA5NDA3NjQ2Nn0.4TDEL2GEw4i0KnTE2Rb7tDWHudHAVMM6IdyWCWCj2jw";

export const supabase = createClient(supabaseUrl, supabaseKey);
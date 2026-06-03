export function ErrorState({ message }: { message: string }) {
  return (
    <div className="rounded border border-red-800 bg-red-950/40 p-4 text-red-200" role="alert">
      {message}
    </div>
  );
}

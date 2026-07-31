export function classifyFavoriteError(error) {
  if (error.status === 401 || error.status === 403) {
    return { message: "Sign in required.", refetch: false, authenticationRequired: true };
  }
  if (error.status === 404) {
    return { message: null, refetch: true, authenticationRequired: false };
  }
  if (error.status === 409) {
    const messages = Object.values(error.data?.errors ?? {}).flat();
    return {
      message: messages.join(" ") || "The favorite limit has been reached.",
      refetch: false,
      authenticationRequired: false,
    };
  }
  return { message: "The favorite could not be changed.", refetch: false, authenticationRequired: false };
}

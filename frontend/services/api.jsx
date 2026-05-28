export async function analyzeTicket(ticketText) {
  console.log ('sending text :'+ticketText)
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

  const response = await fetch(`${API_BASE_URL}/ticket`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ "text": ticketText }),
  });

  if (!response.ok) {
    throw new Error("Failed to analyze ticket");
  }
//   console.log ('received response: '+ response.json())
  return response.json();
}

export async function handlePopulateDBs() {
  console.log ('api.handlePopulateDBs: sending a request to autopopulate')
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

  const response = await fetch(`${API_BASE_URL}/populateDBs`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ "text": "handlePopulate" }),
  });

  if (!response.ok) {
    throw new Error("Failed to analyze ticket");
  }
//   console.log ('received response: '+ response.json())
  return response.json();


}

export async function handleClearDBs() {
  console.log ('api.handleClearDBs: sending a request to autoClear')
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

  const response = await fetch(`${API_BASE_URL}/clearDBs`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ "text": "handleClearDBs" }),
  });

  if (!response.ok) {
    throw new Error("Failed to analyze ticket");
  }
//   console.log ('received response: '+ response.json())
  return response.json();
}

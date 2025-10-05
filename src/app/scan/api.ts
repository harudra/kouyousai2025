type Visitor = {
  visitor_id: string;
};

type VisitPayload = {
  visitor_id: string;
  day: "first" | "second";
  visited: boolean;
};

export async function upsertVisited(payload: VisitPayload) {
  try {
    const endpointUrl = process.env.NEXT_PUBLIC_ENDPOINT_URL;
    const res = await fetch(`${endpointUrl}/upsert_visited`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Failed to upsert visited");
    }

    const data = await res.json();
    return data;
  } catch (error) {
    console.error("Error:", error);
  }
}

export async function readVisitor(payload: Visitor) {
  try {
    const endpointUrl = process.env.NEXT_PUBLIC_ENDPOINT_URL;
    const res = await fetch(`${endpointUrl}/read_visitor`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Failed to read visitor");
    }

    const data = await res.json();
    return data;
  } catch (error) {
    console.error("Error:", error);
  }
}

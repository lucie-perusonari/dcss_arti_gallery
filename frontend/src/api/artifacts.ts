import type {
  Artifact,
  ArtifactFilters,
  ArtifactFiltersMetadata,
  ArtifactType,
} from "../types/artifact";

const API_BASE_URL = (import.meta.env.VITE_ARTIFACT_API_URL ?? "").trim();
const ARTIFACTS_PER_DISPLAY_CATEGORY_LIMIT = 70;
const ARTIFACTS_PAGE_LIMIT = 1000;

type ArtifactResponse = {
  artifacts: Artifact[];
};

export type PlayerArtifactsRequest = {
  nickname: string;
};

export type PlayerArtifactsResponse = {
  nickname: string;
  status: "completed" | "failed";
  message?: string;
  artifactCount?: number;
  error?: string;
  artifacts?: Artifact[];
};

const apiUrl = (path: string) => `${API_BASE_URL.replace(/\/$/, "")}${path}`;

function requireApiBaseUrl() {
  if (!API_BASE_URL) {
    throw new Error("VITE_ARTIFACT_API_URL is required");
  }
}

async function apiError(response: Response, fallback: string) {
  let detail = "";
  try {
    const data = (await response.json()) as { detail?: unknown };
    detail = typeof data.detail === "string" ? `: ${data.detail}` : "";
  } catch {
    detail = "";
  }
  return new Error(`${fallback} with ${response.status}${detail}`);
}

async function fetchArtifacts(
  params: URLSearchParams,
  limit = ARTIFACTS_PER_DISPLAY_CATEGORY_LIMIT,
): Promise<Artifact[]> {
  params.set("limit", String(limit));

  const response = await fetch(apiUrl(`/artifacts?${params.toString()}`));
  if (!response.ok) {
    throw await apiError(response, "Artifact API failed");
  }

  const data = (await response.json()) as ArtifactResponse;
  return data.artifacts;
}

async function fetchAllArtifacts(
  params: URLSearchParams,
  maxArtifacts?: number,
): Promise<Artifact[]> {
  const artifacts: Artifact[] = [];
  let offset = 0;

  while (true) {
    const pageParams = new URLSearchParams(params);
    pageParams.set("offset", String(offset));
    const remainingArtifacts =
      maxArtifacts === undefined
        ? ARTIFACTS_PAGE_LIMIT
        : maxArtifacts - artifacts.length;
    if (remainingArtifacts <= 0) break;

    const page = await fetchArtifacts(
      pageParams,
      Math.min(ARTIFACTS_PAGE_LIMIT, remainingArtifacts),
    );
    artifacts.push(...page);

    if (page.length < ARTIFACTS_PAGE_LIMIT) break;
    offset += ARTIFACTS_PAGE_LIMIT;
  }

  return artifacts;
}

function uniqueArtifacts(artifactGroups: Artifact[][]): Artifact[] {
  const byId = new Map<string, Artifact>();
  for (const artifact of artifactGroups.flat()) {
    byId.set(artifact.id, artifact);
  }
  return Array.from(byId.values()).sort(
    (left, right) => right.score.total - left.score.total,
  );
}

export const artifactApi = {
  async listArtifacts(filters: ArtifactFilters): Promise<Artifact[]> {
    requireApiBaseUrl();

    const params = new URLSearchParams();
    if (filters.search.trim()) params.set("q", filters.search.trim());
    if (filters.player.trim()) params.set("player", filters.player.trim());
    params.set("since", filters.timeRange);

    const filtersMetadata = await this.listFilters();
    const types = (
      filters.type === "all" ? filtersMetadata.types : [filters.type]
    ).filter(
      (type): type is ArtifactType => type !== "all",
    );
    const artifactGroups = await Promise.all(
      types.flatMap((type) =>
        displayCategoriesForType(filtersMetadata, type).map((displayCategory) => {
          const typedParams = new URLSearchParams(params);
          typedParams.set("type", type);
          typedParams.set("displayCategory", displayCategory);
          return fetchArtifacts(typedParams, ARTIFACTS_PER_DISPLAY_CATEGORY_LIMIT);
        }),
      ),
    );
    return uniqueArtifacts(artifactGroups);
  },

  async getArtifact(id: string): Promise<Artifact | null> {
    requireApiBaseUrl();

    const response = await fetch(apiUrl(`/artifacts/${id}`));
    if (response.status === 404) return null;
    if (!response.ok) {
      throw await apiError(response, "Artifact API failed");
    }

    return (await response.json()) as Artifact;
  },

  async listTypes(): Promise<Array<ArtifactType | "all">> {
    return (await this.listFilters()).types;
  },

  async listFilters(): Promise<ArtifactFiltersMetadata> {
    requireApiBaseUrl();

    const response = await fetch(apiUrl("/filters"));
    if (!response.ok) {
      throw await apiError(response, "Artifact filter API failed");
    }

    const data = (await response.json()) as Partial<ArtifactFiltersMetadata>;
    return {
      types: data.types ?? ["all"],
      displayCategories: data.displayCategories ?? {},
    };
  },

  async listPlayerArtifacts(
    request: PlayerArtifactsRequest,
  ): Promise<PlayerArtifactsResponse> {
    const nickname = request.nickname.trim();
    if (!nickname) {
      throw new Error("Nickname is required");
    }
    requireApiBaseUrl();

    const params = new URLSearchParams({ player: nickname, since: "30d" });
    const artifacts = await fetchAllArtifacts(params);
    return {
      nickname,
      status: "completed",
      message: `Loaded ${artifacts.length} stored artifacts for ${nickname}.`,
      artifactCount: artifacts.length,
      artifacts,
    };
  },
};

function displayCategoriesForType(
  filtersMetadata: ArtifactFiltersMetadata,
  type: ArtifactType,
) {
  const categories = filtersMetadata.displayCategories[type] ?? [];
  return categories.length > 0 ? categories : ["all"];
}

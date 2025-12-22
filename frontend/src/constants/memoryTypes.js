/**
 * Memory Type Constants
 */

export const MEMORY_TYPES = {
  SHORT_TERM: 'short_term',
  SEMANTIC: 'semantic',
  EPISODIC: 'episodic',
  PROFILE: 'profile',
  PROCEDURAL: 'procedural',
};

export const MEMORY_TYPE_LABELS = {
  [MEMORY_TYPES.SHORT_TERM]: 'Conversation History',
  [MEMORY_TYPES.SEMANTIC]: 'Semantic Memory',
  [MEMORY_TYPES.EPISODIC]: 'Episodic Memory',
  [MEMORY_TYPES.PROFILE]: 'User Profile',
  [MEMORY_TYPES.PROCEDURAL]: 'Procedural Patterns',
};

export const MEMORY_TYPE_DESCRIPTIONS = {
  [MEMORY_TYPES.SHORT_TERM]: 'Recent messages in the current conversation',
  [MEMORY_TYPES.SEMANTIC]: 'Key facts and knowledge extracted from conversations',
  [MEMORY_TYPES.EPISODIC]: 'Summaries of past conversation episodes',
  [MEMORY_TYPES.PROFILE]: 'User preferences and personal information',
  [MEMORY_TYPES.PROCEDURAL]: 'Learned patterns and workflows',
};

// Long-term memory types only (excludes short-term)
export const LONG_TERM_MEMORY_TYPES = [
  MEMORY_TYPES.SEMANTIC,
  MEMORY_TYPES.PROFILE,
  MEMORY_TYPES.EPISODIC,
  MEMORY_TYPES.PROCEDURAL,
];

export const ALL_MEMORY_TYPES = Object.values(MEMORY_TYPES);

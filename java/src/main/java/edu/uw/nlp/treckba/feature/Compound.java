package edu.uw.nlp.treckba.feature;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class Compound {

	private static final String UNDERSCORE = "_";
	private final String lemma;
	private final int mentionId;
	private boolean used;

	public Compound(final String lemma, final int mentionId) {
		this.lemma = lemma;
		this.mentionId = mentionId;
		this.used = false;
	}

	public String getLemma() {
		return lemma;
	}

	public int getMentionId() {
		return mentionId;
	}

	public boolean isUsed() {
		return used;
	}

	public void setUsed(final boolean used) {
		this.used = used;
	}

	@Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = prime * result + (lemma == null ? 0 : lemma.hashCode());
		result = prime * result + mentionId;
		return result;
	}

	@Override
	public boolean equals(final Object obj) {
		if (this == obj) {
			return true;
		}
		if (obj == null) {
			return false;
		}
		if (getClass() != obj.getClass()) {
			return false;
		}
		final Compound other = (Compound) obj;
		if (lemma == null) {
			if (other.lemma != null) {
				return false;
			}
		} else if (!lemma.equals(other.lemma)) {
			return false;
		}
		if (mentionId != other.mentionId) {
			return false;
		}
		return true;
	}

	public static Set<String> compoundsToString(final List<Compound> compounds) {
		final Set<String> result = new HashSet<>();
		if (compounds.size() == 0) {
			return result;
		}
		if (compounds.size() == 1) {
			final Compound c = compounds.get(0);
			c.setUsed(true);
			result.add(c.getLemma());
			return result;
		}
		for (int i = 0; i < compounds.size(); i++) {
			final Compound c = compounds.get(i);
			if (c.isUsed()) {
				continue;
			}
			c.setUsed(true);
			if (c.getMentionId() == -1) {
				result.add(c.getLemma());
			} else {
				String partial = c.getLemma();
				for (int j = i + 1; j < compounds.size(); j++) {
					final Compound candidate = compounds.get(j);
					if (candidate.getMentionId() == c.getMentionId()
							&& !candidate.isUsed()) {
						partial += UNDERSCORE + candidate.getLemma();
						candidate.setUsed(true);
					}
				}
				result.add(partial);
			}
		}
		return result;
	}
}

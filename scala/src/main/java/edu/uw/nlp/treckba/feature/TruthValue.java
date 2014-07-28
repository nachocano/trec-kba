package edu.uw.nlp.treckba.feature;

public class TruthValue {

	private Integer relevance;
	private String dateHour;

	public TruthValue(final Integer relevance, final String dateHour) {
		this.relevance = relevance;
		this.dateHour = dateHour;
	}

	public Integer getRelevance() {
		return relevance;
	}

	public void setRelevance(final Integer relevance) {
		this.relevance = relevance;
	}

	public String getDateHour() {
		return dateHour;
	}

	public void setDateHour(final String dateHour) {
		this.dateHour = dateHour;
	}

	@Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = (prime * result)
				+ ((dateHour == null) ? 0 : dateHour.hashCode());
		result = (prime * result)
				+ ((relevance == null) ? 0 : relevance.hashCode());
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
		final TruthValue other = (TruthValue) obj;
		if (dateHour == null) {
			if (other.dateHour != null) {
				return false;
			}
		} else if (!dateHour.equals(other.dateHour)) {
			return false;
		}
		if (relevance == null) {
			if (other.relevance != null) {
				return false;
			}
		} else if (!relevance.equals(other.relevance)) {
			return false;
		}
		return true;
	}

}

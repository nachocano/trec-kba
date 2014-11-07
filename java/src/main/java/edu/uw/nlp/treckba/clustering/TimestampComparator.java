package edu.uw.nlp.treckba.clustering;

import java.util.Comparator;

public class TimestampComparator implements Comparator<ClusterExample> {

	@Override
	public int compare(final ClusterExample o1, final ClusterExample o2) {
		return Long.compare(o1.getTimestamp(), o2.getTimestamp());
	}

}

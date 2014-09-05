package edu.uw.nlp.treckba.clustering;

public class ClusteringConstants {

	public static final int NR_FEATURES = 25;
	public static final int EMBEDDING_DIM = 300;
	public static final int D = 629;
	public static final float START_TIMELINESS = 0.5f;
	public static final String WHITE_SPACE = " ";

	public static final int BUCKETS = 7;
	public static final int ONE_HOUR_BUCKET = 0;
	public static final int FIVE_HOURS_BUCKET = 1;
	public static final int TEN_HOURS_BUCKET = 2;
	public static final int ONE_DAY_BUCKET = 3;
	public static final int TWO_DAYS_BUCKET = 4;
	public static final int FOUR_DAYS_BUCKET = 5;
	public static final int ONE_WEEK_BUCKET = 6;

	public static final long SECONDS_IN_HOUR = 60 * 60;
	public static final long SECONDS_IN_FIVE_HOURS = SECONDS_IN_HOUR * 5;
	public static final long SECONDS_IN_TEN_HOURS = SECONDS_IN_HOUR * 10;
	public static final long SECONDS_IN_DAY = SECONDS_IN_HOUR * 24;
	public static final long SECONDS_IN_TWO_DAYS = SECONDS_IN_DAY * 2;
	public static final long SECONDS_IN_FOUR_DAYS = SECONDS_IN_DAY * 4;
	public static final long SECONDS_IN_WEEK = SECONDS_IN_DAY * 7;

}

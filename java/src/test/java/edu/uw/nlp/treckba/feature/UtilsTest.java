package edu.uw.nlp.treckba.feature;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.junit.Assert;
import org.junit.Test;

public class UtilsTest {

	@Test
	public void testGetMostFrequent() {
		final Map<TruthKey, List<TruthValue>> noisy = new HashMap<>();
		final List<TruthValue> list1 = new ArrayList<>();
		list1.add(new TruthValue(5, "date1"));
		list1.add(new TruthValue(5, "date1"));
		list1.add(new TruthValue(5, "date1"));
		final TruthKey truthKey1 = new TruthKey("streamid1", "targetId1");
		noisy.put(truthKey1, list1);

		final List<TruthValue> list2 = new ArrayList<>();
		list2.add(new TruthValue(2, "date2"));
		final TruthKey truthKey2 = new TruthKey("streamid2", "targetId2");
		noisy.put(truthKey2, list2);

		final List<TruthValue> list3 = new ArrayList<>();
		list3.add(new TruthValue(1, "date3"));
		list3.add(new TruthValue(2, "date3"));
		list3.add(new TruthValue(4, "date3"));
		final TruthKey truthKey3 = new TruthKey("streamid3", "targetId3");
		noisy.put(truthKey3, list3);

		final Map<TruthKey, TruthValue> actual = Utils.getMostFrequent(noisy);

		Assert.assertEquals(Integer.valueOf(5), actual.get(truthKey1)
				.getRelevance());
		Assert.assertEquals(Integer.valueOf(2), actual.get(truthKey2)
				.getRelevance());
		Assert.assertEquals(Integer.valueOf(4), actual.get(truthKey3)
				.getRelevance());

		Assert.assertEquals("date1", actual.get(truthKey1).getDateHour());
		Assert.assertEquals("date2", actual.get(truthKey2).getDateHour());
		Assert.assertEquals("date3", actual.get(truthKey3).getDateHour());

	}
}

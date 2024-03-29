/**
 * Autogenerated by Thrift Compiler (0.9.1)
 *
 * DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
 *  @generated
 */
package edu.uw.nlp.treckba.gen;


import java.util.Map;
import java.util.HashMap;
import org.apache.thrift.TEnum;

/**
 * Different tagging tools have different strings for labeling the
 * various common entity types.  To avoid ambiguity, we define a
 * canonical list here, which we will surely have to expand over time
 * as new taggers recognize new types of entities.
 * 
 * LOC: physical location
 * 
 * MISC: uncategorized named entities, e.g. Civil War for Stanford CoreNLP
 */
public enum EntityType implements org.apache.thrift.TEnum {
  PER(0),
  ORG(1),
  LOC(2),
  TIME(5),
  DATE(6),
  MONEY(7),
  PERCENT(8),
  MISC(9),
  GPE(10),
  FAC(11),
  VEH(12),
  WEA(13),
  phone(14),
  email(15),
  URL(16),
  CUSTOM_TYPE(17),
  LIST(18);

  private final int value;

  private EntityType(int value) {
    this.value = value;
  }

  /**
   * Get the integer value of this enum value, as defined in the Thrift IDL.
   */
  public int getValue() {
    return value;
  }

  /**
   * Find a the enum type by its integer value, as defined in the Thrift IDL.
   * @return null if the value is not found.
   */
  public static EntityType findByValue(int value) { 
    switch (value) {
      case 0:
        return PER;
      case 1:
        return ORG;
      case 2:
        return LOC;
      case 5:
        return TIME;
      case 6:
        return DATE;
      case 7:
        return MONEY;
      case 8:
        return PERCENT;
      case 9:
        return MISC;
      case 10:
        return GPE;
      case 11:
        return FAC;
      case 12:
        return VEH;
      case 13:
        return WEA;
      case 14:
        return phone;
      case 15:
        return email;
      case 16:
        return URL;
      case 17:
        return CUSTOM_TYPE;
      case 18:
        return LIST;
      default:
        return null;
    }
  }
}

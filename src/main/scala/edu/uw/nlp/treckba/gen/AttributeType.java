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
 * Attributes are based primarily on TAC KBP, see also saved in this directory
 * http://surdeanu.info/kbp2013/TAC_2013_KBP_Slot_Descriptions_1.0.pdf
 * 
 * Only slots that are not resolvable to unique entities are listed
 * here as attributes.  Most slots are relations, so see RelationType.
 */
public enum AttributeType implements org.apache.thrift.TEnum {
  PER_AGE(0),
  PER_GENDER(1),
  PER_ALTERNATE_NAMES(3),
  PER_CAUSE_OF_DEATH(4),
  PER_TITLE(5),
  PER_CHARGES(6),
  ORG_ALTERNATE_NAMES(7),
  ORG_NUMBER_OF_EMPLOYEES_MEMBERS(8);

  private final int value;

  private AttributeType(int value) {
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
  public static AttributeType findByValue(int value) { 
    switch (value) {
      case 0:
        return PER_AGE;
      case 1:
        return PER_GENDER;
      case 3:
        return PER_ALTERNATE_NAMES;
      case 4:
        return PER_CAUSE_OF_DEATH;
      case 5:
        return PER_TITLE;
      case 6:
        return PER_CHARGES;
      case 7:
        return ORG_ALTERNATE_NAMES;
      case 8:
        return ORG_NUMBER_OF_EMPLOYEES_MEMBERS;
      default:
        return null;
    }
  }
}

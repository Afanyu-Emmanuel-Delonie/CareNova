class UserProfile {
  final String email;
  final String role;
  final String firstName;
  final String lastName;
  final String phoneNumber;
  final String address;
  final String? profilePicture;
  final PatientData? patientData;

  UserProfile({
    required this.email,
    required this.role,
    required this.firstName,
    required this.lastName,
    required this.phoneNumber,
    required this.address,
    this.profilePicture,
    this.patientData,
  });

  String get fullName => '$firstName $lastName'.trim();

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      email: json['email'] ?? '',
      role: json['role'] ?? '',
      firstName: json['first_name'] ?? '',
      lastName: json['last_name'] ?? '',
      phoneNumber: json['phone_number'] ?? '',
      address: json['address'] ?? '',
      profilePicture: json['profile_picture'],
      patientData: json['patient_data'] != null
          ? PatientData.fromJson(json['patient_data'])
          : null,
    );
  }
}

class PatientData {
  final String? dateOfBirth;
  final String bloodGroup;
  final String allergies;
  final String emergencyContact;

  PatientData({
    this.dateOfBirth,
    required this.bloodGroup,
    required this.allergies,
    required this.emergencyContact,
  });

  factory PatientData.fromJson(Map<String, dynamic> json) {
    return PatientData(
      dateOfBirth: json['date_of_birth'],
      bloodGroup: json['blood_group'] ?? '',
      allergies: json['allergies'] ?? '',
      emergencyContact: json['emergency_contact'] ?? '',
    );
  }
}